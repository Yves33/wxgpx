from collections import namedtuple
import datetime
import math
import os


RECORD_HEADER_NORMAL = 0
RECORD_HEADER_COMPRESSED_TS = 1

MESSAGE_DEFINITION = 1
MESSAGE_DATA = 0

LITTLE_ENDIAN = 0
BIG_ENDIAN = 1

TIMESTAMP_FIELD_DEF_NUM = 253
COMPRESSED_TIMESTAMP_FIELD_NAME = 'timestamp'
COMPRESSED_TIMESTAMP_TYPE_NAME = 'date_time'

UNKNOWN_FIELD_NAME = 'unknown'


class RecordHeader(namedtuple('RecordHeader',
    ('type', 'message_type', 'local_message_type', 'seconds_offset'))):
    # type -- one of RECORD_HEADER_NORMAL, RECORD_HEADER_COMPRESSED_TS
    # message_type -- one of MESSAGE_DEFINITION, MESSAGE_DATA
    # local_message_type -- a number
    #    * for a definition message, the key to store in FitFile().global_messages
    #    * for a data message, the key to look up the associated definition
    # seconds_offset -- for RECORD_HEADER_COMPRESSED_TS, offset in seconds
    # NOTE: Though named similarly, none of these map to the namedtuples below
    __slots__ = ()


class FieldTypeBase(namedtuple('FieldTypeBase', ('num', 'name', 'invalid', 'struct_fmt', 'is_variable_size'))):
    # Yields a singleton if called with just a num
    __slots__ = ()
    _instances = {}

    def __new__(cls, num, *args, **kwargs):
        instance = FieldTypeBase._instances.get(num)
        if instance:
            return instance

        instance = super(FieldTypeBase, cls).__new__(cls, num, *args, **kwargs)
        FieldTypeBase._instances[num] = instance
        return instance

    def get_struct_fmt(self, size):
        if self.is_variable_size:
            return self.struct_fmt % size
        else:
            return self.struct_fmt

    def convert(self, raw_data):
        if callable(self.invalid):
            if self.invalid(raw_data):
                return None
        else:
            if raw_data == self.invalid:
                return None

        if self.name == 'string':
            raw_data = raw_data.rstrip('\x00')

        return raw_data

    @property
    def base(self):
        return self


class FieldType(namedtuple('FieldType', ('name', 'base', 'converter'))):
    # Higher level fields as defined in Profile.xls
    #
    # converter is a dict or a func. If type is uint*z, then converter should
    # look through the value as a bit array and return all found values
    __slots__ = ()
    _instances = {}

    def __new__(cls, name, *args, **kwargs):
        instance = FieldType._instances.get(name)
        if instance:
            return instance

        instance = super(FieldType, cls).__new__(cls, name, *args, **kwargs)
        FieldType._instances[name] = instance
        return instance

    @property
    def get_struct_fmt(self):
        return self.base.get_struct_fmt

    def convert(self, raw_data):
        if self.base.convert(raw_data) is None:
            return None
        elif isinstance(self.converter, dict):
            #if self.base.name in ('uint8z', 'uint16z', 'uint32z'):
            #    XXX -- handle this condition, ie return a list of properties
            return self.converter.get(raw_data, raw_data)
        elif callable(self.converter):
            return self.converter(raw_data)
        else:
            return raw_data


def _field_convert(self, raw_data):
    data = self.type.convert(raw_data)
    if isinstance(data, (int, float)):
        if self.scale:
            data = float(data) / self.scale
        if self.offset:
            data = data - self.offset
    return data


class Field(namedtuple('Field', ('name', 'type', 'units', 'scale', 'offset'))):
    # A name, type, units, scale, offset
    __slots__ = ()
    convert = _field_convert


class DynamicField(namedtuple('DynamicField', ('name', 'type', 'units', 'scale', 'offset', 'possibilities'))):
    # A name, type, units, scale, offset
    # TODO: Describe format of possiblities
    __slots__ = ()
    convert = _field_convert


class AllocatedField(namedtuple('AllocatedField', ('field', 'size'))):
    # A field along with its size
    __slots__ = ()

    @property
    def name(self):
        return self.field.name

    @property
    def type(self):
        return self.field.type


class BoundField(namedtuple('BoundField', ('data', 'raw_data', 'field'))):
    # Convert data
    __slots__ = ()

    def __new__(cls, raw_data, field):
        data = field.convert(raw_data)
        return super(BoundField, cls).__new__(cls, data, raw_data, field)

    @property
    def name(self):
        return self.field.name

    @property
    def type(self):
        return self.field.type

    @property
    def units(self):
        return self.field.units

    def items(self):
        return self.name, self.data


class MessageType(namedtuple('MessageType', ('num', 'name', 'fields'))):
    # TODO: Describe format of fields (dict)
    __slots__ = ()
    _instances = {}

    def __new__(cls, num, *args, **kwargs):
        instance = MessageType._instances.get(num)
        if instance:
            return instance

        try:
            instance = super(MessageType, cls).__new__(cls, num, *args, **kwargs)
        except TypeError:
            # Don't store unknown field types in _instances.
            # this would be a potential memory leak in a long-running parser
            return super(MessageType, cls).__new__(cls, num, 'unknown', None)

        MessageType._instances[num] = instance
        return instance

    @property
    def field_names(self):
        return [f.name for f in self.fields.values()]


class DefinitionRecord(namedtuple('DefinitionRecord', ('header', 'type', 'arch', 'fields'))):
    # arch -- Little endian or big endian
    # fields -- list of AllocatedFields
    # type -- MessageType
    __slots__ = ()

    @property
    def name(self):
        return self.type.name

    @property
    def num(self):
        return self.type.num


class DataRecord(namedtuple('DataRecord', ('header', 'definition', 'fields'))):
    # fields -- list of BoundFields
    __slots__ = ()

    @property
    def name(self):
        return self.definition.name

    @property
    def type(self):
        return self.definition.type

    @property
    def num(self):
        return self.definition.num

    def iteritems(self):
        return (f.items() for f in self.fields)

    def as_dict(self, with_ommited_fields=False):
        d = dict((k, v) for k, v in self.iteritems() if k != UNKNOWN_FIELD_NAME)
        if with_ommited_fields:
            for k in self.type.field_names:
                d.setdefault(k, None)
        return d

    def get_valid_field_names(self):
        return [f.name for f in self.fields if f.name != UNKNOWN_FIELD_NAME and f.data is not None]

    def get_data(self, field_name):
        for field in self.fields:
            if field.name == field_name:
                return field.data
        return None

    def get_units(self, field_name):
        for field in self.fields:
            if field.name == field_name:
                return field.units
        return None


# Definitions from FIT SDK 1.2

FieldTypeBase(0, 'enum', 0xFF, 'B', False)
FieldTypeBase(1, 'sint8', 0x7F, 'b', False)
FieldTypeBase(2, 'uint8', 0xFF, 'B', False)
FieldTypeBase(3, 'sint16', 0x7FFF, 'h', False)
FieldTypeBase(4, 'uint16', 0xFFFF, 'H', False)
FieldTypeBase(5, 'sint32', 0x7FFFFFFF, 'i', False)
FieldTypeBase(6, 'uint32', 0xFFFFFFFF, 'I', False)
FieldTypeBase(7, 'string', lambda x: all([ord(c) == '\x00' for c in x]), '%ds', True)
FieldTypeBase(8, 'float32', math.isnan, 'f', False)
FieldTypeBase(9, 'float64', math.isnan, 'd', False)
FieldTypeBase(10, 'uint8z', 0, 'B', False)
FieldTypeBase(11, 'uint16z', 0, 'H', False)
FieldTypeBase(12, 'uint32z', 0, 'I', False)
FieldTypeBase(13, 'byte', lambda x: all([ord(c) == '\xFF' for c in x]), '%ds', True)


# Custom conversion functions for FieldTypes (specific to FIT SDK 1.2)

# TODO:
#   "0x10000000: if date_time is < 0x10000000 then it is system time (seconds
#   from device power on)" -- not ofr local_date_time
_convert_date_time = lambda x: datetime.datetime.fromtimestamp(631065600 + x)

# TODO: Handle local tz conversion
_convert_local_date_time = lambda x: datetime.datetime.fromtimestamp(631065600 + x)

_convert_bool = lambda x: bool(x)


# XXX -- untested
# see FitSDK1_2.zip:c/examples/decode/decode.c lines 121-150 for an example
def _convert_record_compressed_speed_distance(raw_data):
    first, second, third = (ord(b) for b in raw_data)
    speed = first + (second & 0b1111)
    distance = (third << 4) + ((second & 0b11110000) >> 4)
    return speed / 100. / 1000. * 60. * 60., distance / 16.


class MessageIndexValue(int):
    __slots__ = ('selected',)


def _convert_message_index(raw_data):
    message_index = MessageIndexValue(raw_data & 0x0FFF)
    message_index.selected = bool(raw_data & 0x8000)
    return message_index


class ActivityClassValue(int):
    __slots__ = ('athlete',)


def _convert_activity_class(raw_data):
    activity_class = ActivityClassValue(raw_data & 0x7F)
    activity_class.athlete = bool(raw_data & 0x80)
    return activity_class


# Load in Profile

# XXX -- we do this so ipython doesn't throw an error on __file__.
#try:
#    execfile('profile.def')
#except IOError:
#    execfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profile.def'))


##############################################################################
################   AUTOMATICALLY GENERATED DEFINITION FILE   #################
##############################################################################
#
# profile.def -- Exported FIT SDK Profile Data
# Created on 2011-08-11 13:56:10 by generate_profile.py from Profile.xls
#
##############################################################################
#
# Please define the following functions (types that use them are listed):
#
#  _convert_activity_class
#    * Used by types:
#       - activity_class
#
#  _convert_bool
#    * Used by types:
#       - bool
#
#  _convert_date_time
#    * Used by types:
#       - date_time
#
#  _convert_local_date_time
#    * Used by types:
#       - local_date_time
#
#  _convert_message_index
#    * Used by types:
#       - message_index
#
#  _convert_record_compressed_speed_distance
#    * Used by types:
#       - record-compressed_speed_distance
#
##############################################################################


###########################   BEGIN FIELD TYPES   ############################

FieldType('activity', FieldTypeBase(0), {  # base type: enum
    0: 'manual',
    1: 'auto_multi_sport',
})

FieldType('activity_class', FieldTypeBase(0), _convert_activity_class)  # base type: enum

FieldType('autolap_trigger', FieldTypeBase(0), {  # base type: enum
    0: 'time',
    1: 'distance',
    2: 'position_start',
    3: 'position_lap',
    4: 'position_waypoint',
    5: 'position_marked',
    6: 'off',
})

FieldType('battery_status', FieldTypeBase(2), {  # base type: uint8
    1: 'new',
    2: 'good',
    3: 'ok',
    4: 'low',
    5: 'critical',
})

FieldType('bool', FieldTypeBase(0), _convert_bool)  # base type: enum

FieldType('bp_status', FieldTypeBase(0), {  # base type: enum
    0: 'no_error',
    1: 'error_incomplete_data',
    2: 'error_no_measurement',
    3: 'error_data_out_of_range',
    4: 'error_irregular_heart_rate',
})

FieldType('course_capabilities', FieldTypeBase(12), {  # base type: uint32z
    0x00000001: 'processed',
    0x00000002: 'valid',
    0x00000004: 'time',
    0x00000008: 'distance',
    0x00000010: 'position',
    0x00000020: 'heart_rate',
    0x00000040: 'power',
    0x00000080: 'cadence',
    0x00000100: 'training',
    0x00000200: 'navigation',
})

FieldType('course_point', FieldTypeBase(0), {  # base type: enum
    0: 'generic',
    1: 'summit',
    2: 'valley',
    3: 'water',
    4: 'food',
    5: 'danger',
    6: 'left',
    7: 'right',
    8: 'straight',
    9: 'first_aid',
    10: 'fourth_category',
    11: 'third_category',
    12: 'second_category',
    13: 'first_category',
    14: 'hors_category',
    15: 'sprint',
    16: 'left_fork',
    17: 'right_fork',
    18: 'middle_fork',
})

FieldType('date_time', FieldTypeBase(6), _convert_date_time)  # base type: uint32

FieldType('device_index', FieldTypeBase(2), {  # base type: uint8
    0: 'creator',
})

FieldType('device_type', FieldTypeBase(2), {  # base type: uint8
    1: 'antfs',
    11: 'bike_power',
    12: 'environment_sensor',
    15: 'multi_sport_speed_distance',
    17: 'fitness_equipment',
    18: 'blood_pressure',
    119: 'weight_scale',
    120: 'heart_rate',
    121: 'bike_speed_cadence',
    122: 'bike_cadence',
    123: 'bike_speed',
    124: 'stride_speed_distance',
})

FieldType('display_heart', FieldTypeBase(0), {  # base type: enum
    0: 'bpm',
    1: 'max',
    2: 'reserve',
})

FieldType('display_measure', FieldTypeBase(0), {  # base type: enum
    0: 'metric',
    1: 'statute',
})

FieldType('display_position', FieldTypeBase(0), {  # base type: enum
    0: 'degree',
    1: 'degree_minute',
    2: 'degree_minute_second',
    3: 'austrian_grid',
    4: 'british_grid',
    5: 'dutch_grid',
    6: 'hungarian_grid',
    7: 'finnish_grid',
    8: 'german_grid',
    9: 'icelandic_grid',
    10: 'indonesian_equatorial',
    11: 'indonesian_irian',
    12: 'indonesian_southern',
    13: 'india_zone_0',
    14: 'india_zone_IA',
    15: 'india_zone_IB',
    16: 'india_zone_IIA',
    17: 'india_zone_IIB',
    18: 'india_zone_IIIA',
    19: 'india_zone_IIIB',
    20: 'india_zone_IVA',
    21: 'india_zone_IVB',
    22: 'irish_transverse',
    23: 'irish_grid',
    24: 'loran',
    25: 'maidenhead_grid',
    26: 'mgrs_grid',
    27: 'new_zealand_grid',
    28: 'new_zealand_transverse',
    29: 'qatar_grid',
    30: 'modified_swedish_grid',
    31: 'swedish_grid',
    32: 'south_african_grid',
    33: 'swiss_grid',
    34: 'taiwan_grid',
    35: 'united_states_grid',
    36: 'utm_ups_grid',
    37: 'west_malayan',
    38: 'borneo_rso',
    39: 'estonian_grid',
    40: 'latvian_grid',
    41: 'swedish_ref_99_grid',
})

FieldType('display_power', FieldTypeBase(0), {  # base type: enum
    0: 'watts',
    1: 'percent_ftp',
})

FieldType('event', FieldTypeBase(0), {  # base type: enum
    0: 'timer',
    3: 'workout',
    4: 'workout_step',
    5: 'power_down',
    6: 'power_up',
    7: 'off_course',
    8: 'session',
    9: 'lap',
    10: 'course_point',
    11: 'battery',
    12: 'virtual_partner_pace',
    13: 'hr_high_alert',
    14: 'hr_low_alert',
    15: 'speed_high_alert',
    16: 'speed_low_alert',
    17: 'cad_high_alert',
    18: 'cad_low_alert',
    19: 'power_high_alert',
    20: 'power_low_alert',
    21: 'recovery_hr',
    22: 'battery_low',
    23: 'time_duration_alert',
    24: 'distance_duration_alert',
    25: 'calorie_duration_alert',
    26: 'activity',
    27: 'fitness_equipment',
})

FieldType('event_type', FieldTypeBase(0), {  # base type: enum
    0: 'start',
    1: 'stop',
    2: 'consecutive_depreciated',
    3: 'marker',
    4: 'stop_all',
    5: 'begin_depreciated',
    6: 'end_depreciated',
    7: 'end_all_depreciated',
    8: 'stop_disable',
    9: 'stop_disable_all',
})

FieldType('file', FieldTypeBase(0), {  # base type: enum
    1: 'device',
    2: 'settings',
    3: 'sport',
    4: 'activity',
    5: 'workout',
    6: 'course',
    9: 'weight',
    10: 'totals',
    11: 'goals',
    14: 'blood_pressure',
    20: 'activity_summary',
})

FieldType('file_flags', FieldTypeBase(10), {  # base type: uint8z
    0x02: 'read',
    0x04: 'write',
    0x08: 'erase',
})

FieldType('fitness_equipment_state', FieldTypeBase(0), {  # base type: enum
    0: 'ready',
    1: 'in_use',
    2: 'paused',
    3: 'unknown',
})

FieldType('garmin_product', FieldTypeBase(4), {  # base type: uint16
    1: 'hrm1',
    2: 'axh01',
    3: 'axb01',
    4: 'axb02',
    5: 'hrm2ss',
    6: 'dsi_alf02',
    717: 'fr405',
    782: 'fr50',
    988: 'fr60',
    1011: 'dsi_alf01',
    1018: 'fr310xt',
    1036: 'edge500',
    1124: 'fr110',
    1169: 'edge800',
    1253: 'chirp',
    10007: 'sdm4',
    20119: 'training_center',
    65534: 'connect',
})

FieldType('gender', FieldTypeBase(0), {  # base type: enum
    0: 'female',
    1: 'male',
})

FieldType('goal', FieldTypeBase(0), {  # base type: enum
    0: 'time',
    1: 'distance',
    2: 'calories',
    3: 'frequency',
    4: 'steps',
})

FieldType('goal_recurrence', FieldTypeBase(0), {  # base type: enum
    0: 'off',
    1: 'daily',
    2: 'weekly',
    3: 'monthly',
    4: 'yearly',
    5: 'custom',
})

FieldType('hr_type', FieldTypeBase(0), {  # base type: enum
    0: 'normal',
    1: 'irregular',
})

FieldType('hr_zone_calc', FieldTypeBase(0), {  # base type: enum
    0: 'custom',
    1: 'percent_max_hr',
    2: 'percent_hrr',
})

FieldType('intensity', FieldTypeBase(0), {  # base type: enum
    0: 'active',
    1: 'rest',
    2: 'warmup',
    3: 'cooldown',
})

FieldType('language', FieldTypeBase(0), {  # base type: enum
    0: 'english',
    1: 'french',
    2: 'italian',
    3: 'german',
    4: 'spanish',
    5: 'croatian',
    6: 'czech',
    7: 'danish',
    8: 'dutch',
    9: 'finnish',
    10: 'greek',
    11: 'hungarian',
    12: 'norwegian',
    13: 'polish',
    14: 'portuguese',
    15: 'slovakian',
    16: 'slovenian',
    17: 'swedish',
    18: 'russian',
    19: 'turkish',
    20: 'latvian',
    21: 'ukrainian',
    22: 'arabic',
    23: 'farsi',
    24: 'bulgarian',
    25: 'romanian',
    254: 'custom',
})

FieldType('lap_trigger', FieldTypeBase(0), {  # base type: enum
    0: 'manual',
    1: 'time',
    2: 'distance',
    3: 'position_start',
    4: 'position_lap',
    5: 'position_waypoint',
    6: 'position_marked',
    7: 'session_end',
    8: 'fitness_equipment',
})

FieldType('local_date_time', FieldTypeBase(6), _convert_local_date_time)  # base type: uint32

FieldType('manufacturer', FieldTypeBase(4), {  # base type: uint16
    1: 'garmin',
    2: 'garmin_fr405_antfs',
    3: 'zephyr',
    4: 'dayton',
    5: 'idt',
    6: 'srm',
    7: 'quarq',
    8: 'ibike',
    9: 'saris',
    10: 'spark_hk',
    11: 'tanita',
    12: 'echowell',
    13: 'dynastream_oem',
    14: 'nautilus',
    15: 'dynastream',
    16: 'timex',
    17: 'metrigear',
    18: 'xelic',
    19: 'beurer',
    20: 'cardiosport',
    21: 'a_and_d',
    22: 'hmm',
    23: 'suunto',
    24: 'thita_elektronik',
    25: 'gpulse',
    26: 'clean_mobile',
    27: 'pedal_brain',
    28: 'peaksware',
    29: 'saxonar',
    30: 'lemond_fitness',
    31: 'dexcom',
    32: 'wahoo_fitness',
    33: 'octane_fitness',
})

FieldType('mesg_count', FieldTypeBase(0), {  # base type: enum
    0: 'num_per_file',
    1: 'max_per_file',
    2: 'max_per_file_type',
})

FieldType('mesg_num', FieldTypeBase(4), {  # base type: uint16
    0: 'file_id',
    1: 'capabilities',
    2: 'device_settings',
    3: 'user_profile',
    4: 'hrm_profile',
    5: 'sdm_profile',
    6: 'bike_profile',
    7: 'zones_target',
    8: 'hr_zone',
    9: 'power_zone',
    10: 'met_zone',
    12: 'sport',
    15: 'goal',
    18: 'session',
    19: 'lap',
    20: 'record',
    21: 'event',
    23: 'device_info',
    26: 'workout',
    27: 'workout_step',
    30: 'weight_scale',
    31: 'course',
    32: 'course_point',
    33: 'totals',
    34: 'activity',
    35: 'software',
    37: 'file_capabilities',
    38: 'mesg_capabilities',
    39: 'field_capabilities',
    49: 'file_creator',
    51: 'blood_pressure',
})

FieldType('message_index', FieldTypeBase(4), _convert_message_index)  # base type: uint16

FieldType('pwr_zone_calc', FieldTypeBase(0), {  # base type: enum
    0: 'custom',
    1: 'percent_ftp',
})

FieldType('record-compressed_speed_distance', FieldTypeBase(13), _convert_record_compressed_speed_distance)  # base type: byte

FieldType('session_trigger', FieldTypeBase(0), {  # base type: enum
    0: 'activity_end',
    1: 'manual',
    2: 'auto_multi_sport',
    3: 'fitness_equipment',
})

FieldType('sport', FieldTypeBase(0), {  # base type: enum
    0: 'generic',
    1: 'running',
    2: 'cycling',
    3: 'transition',
    4: 'fitness_equipment',
    5: 'swimming',
    254: 'all',
})

FieldType('sport_bits_0', FieldTypeBase(10), {  # base type: uint8z
    0x01: 'generic',
    0x02: 'running',
    0x04: 'cycling',
    0x08: 'transition',
    0x10: 'fitness_equipment',
    0x20: 'swimming',
})

FieldType('sub_sport', FieldTypeBase(0), {  # base type: enum
    0: 'generic',
    1: 'treadmill',
    2: 'street',
    3: 'trail',
    4: 'track',
    5: 'spin',
    6: 'indoor_cycling',
    7: 'road',
    8: 'mountain',
    9: 'downhill',
    10: 'recumbent',
    11: 'cyclocross',
    12: 'hand_cycling',
    13: 'track_cycling',
    14: 'indoor_rowing',
    15: 'elliptical',
    16: 'stair_climbing',
    17: 'lap_swimming',
    18: 'open_water',
    254: 'all',
})

FieldType('timer_trigger', FieldTypeBase(0), {  # base type: enum
    0: 'manual',
    1: 'auto',
    2: 'fitness_equipment',
})

FieldType('user_local_id', FieldTypeBase(4), {  # base type: uint16
    0x0001: 'local_min',
    0x000F: 'local_max',
    0x0010: 'stationary_min',
    0x00FF: 'stationary_max',
    0x0100: 'portable_min',
    0xFFFE: 'portable_max',
})

FieldType('weight', FieldTypeBase(4), {  # base type: uint16
    0xFFFE: 'calculating',
})

FieldType('wkt_step_duration', FieldTypeBase(0), {  # base type: enum
    0: 'time',
    1: 'distance',
    2: 'hr_less_than',
    3: 'hr_greater_than',
    4: 'calories',
    5: 'open',
    6: 'repeat_until_steps_cmplt',
    7: 'repeat_until_time',
    8: 'repeat_until_distance',
    9: 'repeat_until_calories',
    10: 'repeat_until_hr_less_than',
    11: 'repeat_until_hr_greater_than',
    12: 'repeat_until_power_less_than',
    13: 'repeat_until_power_greater_than',
    14: 'power_less_than',
    15: 'power_greater_than',
})

FieldType('wkt_step_target', FieldTypeBase(0), {  # base type: enum
    0: 'speed',
    1: 'heart_rate',
    2: 'open',
    3: 'cadence',
    4: 'power',
    5: 'grade',
    6: 'resistance',
})

FieldType('workout_capabilities', FieldTypeBase(12), {  # base type: uint32z
    0x00000001: 'interval',
    0x00000002: 'custom',
    0x00000004: 'fitness_equipment',
    0x00000008: 'firstbeat',
    0x00000010: 'new_leaf',
    0x00000020: 'tcx',
    0x00000080: 'speed',
    0x00000100: 'heart_rate',
    0x00000200: 'distance',
    0x00000400: 'cadence',
    0x00000800: 'power',
    0x00001000: 'grade',
    0x00002000: 'resistance',
    0x00004000: 'protected',
})

FieldType('workout_hr', FieldTypeBase(6), {  # base type: uint32
    100: 'bpm_offset',
})

FieldType('workout_power', FieldTypeBase(6), {  # base type: uint32
    1000: 'watts_offset',
})


##########################   BEGIN MESSAGE TYPES   ###########################

MessageType(0, 'file_id', {
    0: Field('type', FieldType('file'), None, None, None),  # base type: enum
    1: Field('manufacturer', FieldType('manufacturer'), None, None, None),  # base type: uint16
    2: DynamicField('product', FieldTypeBase(4), None, None, None, {  # base type: uint16
        'manufacturer': {
            'dynastream': Field('garmin_product', FieldType('garmin_product'), None, None, None),  # base type: uint16
            'dynastream_oem': Field('garmin_product', FieldType('garmin_product'), None, None, None),  # base type: uint16
            'garmin': Field('garmin_product', FieldType('garmin_product'), None, None, None),  # base type: uint16
        },
    }),
    3: Field('serial_number', FieldTypeBase(12), None, None, None),  # base type: uint32z
    4: Field('time_created', FieldType('date_time'), None, None, None),  # base type: uint32
    5: Field('number', FieldTypeBase(4), None, None, None),  # base type: uint16
})

MessageType(1, 'capabilities', {
    0: Field('languages', FieldTypeBase(10), None, None, None),  # base type: uint8z
    1: Field('sports', FieldType('sport_bits_0'), None, None, None),  # base type: uint8z
    21: Field('workouts_supported', FieldType('workout_capabilities'), None, None, None),  # base type: uint32z
})

MessageType(2, 'device_settings', {
    1: Field('utc_offset', FieldTypeBase(6), None, None, None),  # base type: uint32
})

MessageType(3, 'user_profile', {
    0: Field('friendly_name', FieldTypeBase(7), None, None, None),  # base type: string
    1: Field('gender', FieldType('gender'), None, None, None),  # base type: enum
    2: Field('age', FieldTypeBase(2), 'years', None, None),  # base type: uint8
    3: Field('height', FieldTypeBase(2), 'm', 100, None),  # base type: uint8
    4: Field('weight', FieldTypeBase(4), 'kg', 10, None),  # base type: uint16
    5: Field('language', FieldType('language'), None, None, None),  # base type: enum
    6: Field('elev_setting', FieldType('display_measure'), None, None, None),  # base type: enum
    7: Field('weight_setting', FieldType('display_measure'), None, None, None),  # base type: enum
    8: Field('resting_heart_rate', FieldTypeBase(2), 'bpm', None, None),  # base type: uint8
    9: Field('default_max_running_heart_rate', FieldTypeBase(2), 'bpm', None, None),  # base type: uint8
    10: Field('default_max_biking_heart_rate', FieldTypeBase(2), 'bpm', None, None),  # base type: uint8
    11: Field('default_max_heart_rate', FieldTypeBase(2), 'bpm', None, None),  # base type: uint8
    12: Field('hr_setting', FieldType('display_heart'), None, None, None),  # base type: enum
    13: Field('speed_setting', FieldType('display_measure'), None, None, None),  # base type: enum
    14: Field('dist_setting', FieldType('display_measure'), None, None, None),  # base type: enum
    16: Field('power_setting', FieldType('display_power'), None, None, None),  # base type: enum
    17: Field('activity_class', FieldType('activity_class'), None, None, None),  # base type: enum
    18: Field('position_setting', FieldType('display_position'), None, None, None),  # base type: enum
    21: Field('temperature_setting', FieldType('display_measure'), None, None, None),  # base type: enum
    22: Field('local_id', FieldType('user_local_id'), None, None, None),  # base type: uint16
    23: Field('global_id', FieldTypeBase(13), None, None, None),  # base type: byte
    254: Field('message_index', FieldType('message_index'), None, None, None),  # base type: uint16
})

MessageType(4, 'hrm_profile', {
    0: Field('enabled', FieldType('bool'), None, None, None),  # base type: enum
    1: Field('hrm_ant_id', FieldTypeBase(11), None, None, None),  # base type: uint16z
    254: Field('message_index', FieldType('message_index'), None, None, None),  # base type: uint16
})

MessageType(5, 'sdm_profile', {
    0: Field('enabled', FieldType('bool'), None, None, None),  # base type: enum
    1: Field('sdm_ant_id', FieldTypeBase(11), None, None, None),  # base type: uint16z
    2: Field('sdm_cal_factor', FieldTypeBase(4), '%', 10, None),  # base type: uint16
    3: Field('odometer', FieldTypeBase(6), 'm', 100, None),  # base type: uint32
    4: Field('speed_source', FieldType('bool'), None, None, None),  # base type: enum
    254: Field('message_index', FieldType('message_index'), None, None, None),  # base type: uint16
})

MessageType(6, 'bike_profile', {
    0: Field('name', FieldTypeBase(7), None, None, None),  # base type: string
    1: Field('sport', FieldType('sport'), None, None, None),  # base type: enum
    2: Field('sub_sport', FieldType('sub_sport'), None, None, None),  # base type: enum
    3: Field('odometer', FieldTypeBase(6), 'm', 100, None),  # base type: uint32
    4: Field('bike_spd_ant_id', FieldTypeBase(11), None, None, None),  # base type: uint16z
    5: Field('bike_cad_ant_id', FieldTypeBase(11), None, None, None),  # base type: uint16z
    6: Field('bike_spdcad_ant_id', FieldTypeBase(11), None, None, None),  # base type: uint16z
    7: Field('bike_power_ant_id', FieldTypeBase(11), None, None, None),  # base type: uint16z
    8: Field('custom_wheelsize', FieldTypeBase(4), 'm', 1000, None),  # base type: uint16
    9: Field('auto_wheelsize', FieldTypeBase(4), 'm', 1000, None),  # base type: uint16
    10: Field('bike_weight', FieldTypeBase(4), 'kg', 10, None),  # base type: uint16
    11: Field('power_cal_factor', FieldTypeBase(4), '%', 10, None),  # base type: uint16
    12: Field('auto_wheel_cal', FieldType('bool'), None, None, None),  # base type: enum
    13: Field('auto_power_zero', FieldType('bool'), None, None, None),  # base type: enum
    14: Field('id', FieldTypeBase(2), None, None, None),  # base type: uint8
    15: Field('spd_enabled', FieldType('bool'), None, None, None),  # base type: enum
    16: Field('cad_enabled', FieldType('bool'), None, None, None),  # base type: enum
    17: Field('spdcad_enabled', FieldType('bool'), None, None, None),  # base type: enum
    18: Field('power_enabled', FieldType('bool'), None, None, None),  # base type: enum
    254: Field('message_index', FieldType('message_index'), None, None, None),  # base type: uint16
})

MessageType(7, 'zones_target', {
    1: Field('max_heart_rate', FieldTypeBase(2), None, None, None),  # base type: uint8
    2: Field('threshold_heart_rate', FieldTypeBase(2), None, None, None),  # base type: uint8
    3: Field('functional_threshold_power', FieldTypeBase(4), None, None, None),  # base type: uint16
    5: Field('hr_calc_type', FieldType('hr_zone_calc'), None, None, None),  # base type: enum
    7: Field('pwr_calc_type', FieldType('pwr_zone_calc'), None, None, None),  # base type: enum
})

MessageType(8, 'hr_zone', {
    1: Field('high_bpm', FieldTypeBase(2), 'bpm', None, None),  # base type: uint8
    2: Field('name', FieldTypeBase(7), None, None, None),  # base type: string
    254: Field('message_index', FieldType('message_index'), None, None, None),  # base type: uint16
})

MessageType(9, 'power_zone', {
    1: Field('high_value', FieldTypeBase(4), 'watts', None, None),  # base type: uint16
    2: Field('name', FieldTypeBase(7), None, None, None),  # base type: string
    254: Field('message_index', FieldType('message_index'), None, None, None),  # base type: uint16
})

MessageType(10, 'met_zone', {
    1: Field('high_bpm', FieldTypeBase(2), None, None, None),  # base type: uint8
    2: Field('calories', FieldTypeBase(4), 'kcal / min', 10, None),  # base type: uint16
    3: Field('fat_calories', FieldTypeBase(2), 'kcal / min', 10, None),  # base type: uint8
    254: Field('message_index', FieldType('message_index'), None, None, None),  # base type: uint16
})

MessageType(12, 'sport', {
    0: Field('sport', FieldType('sport'), None, None, None),  # base type: enum
    1: Field('sub_sport', FieldType('sub_sport'), None, None, None),  # base type: enum
    3: Field('name', FieldTypeBase(7), None, None, None),  # base type: string
})

MessageType(15, 'goal', {
    0: Field('sport', FieldType('sport'), None, None, None),  # base type: enum
    1: Field('sub_sport', FieldType('sub_sport'), None, None, None),  # base type: enum
    2: Field('start_date', FieldType('date_time'), None, None, None),  # base type: uint32
    3: Field('end_date', FieldType('date_time'), None, None, None),  # base type: uint32
    4: Field('type', FieldType('goal'), None, None, None),  # base type: enum
    5: Field('value', FieldTypeBase(6), None, None, None),  # base type: uint32
    6: Field('repeat', FieldType('bool'), None, None, None),  # base type: enum
    7: Field('target_value', FieldTypeBase(6), None, None, None),  # base type: uint32
    8: Field('recurrence', FieldType('goal_recurrence'), None, None, None),  # base type: enum
    9: Field('recurrence_value', FieldTypeBase(4), None, None, None),  # base type: uint16
    10: Field('enabled', FieldType('bool'), None, None, None),  # base type: enum
    254: Field('message_index', FieldType('message_index'), None, None, None),  # base type: uint16
})

MessageType(18, 'session', {
    0: Field('event', FieldType('event'), None, None, None),  # base type: enum
    1: Field('event_type', FieldType('event_type'), None, None, None),  # base type: enum
    2: Field('start_time', FieldType('date_time'), None, None, None),  # base type: uint32
    3: Field('start_position_lat', FieldTypeBase(5), 'semicircles', None, None),  # base type: sint32
    4: Field('start_position_long', FieldTypeBase(5), 'semicircles', None, None),  # base type: sint32
    5: Field('sport', FieldType('sport'), None, None, None),  # base type: enum
    6: Field('sub_sport', FieldType('sub_sport'), None, None, None),  # base type: enum
    7: Field('total_elapsed_time', FieldTypeBase(6), 's', 1000, None),  # base type: uint32
    8: Field('total_timer_time', FieldTypeBase(6), 's', 1000, None),  # base type: uint32
    9: Field('total_distance', FieldTypeBase(6), 'm', 100, None),  # base type: uint32
    10: DynamicField('total_cycles', FieldTypeBase(6), 'cycles', None, None, {  # base type: uint32
        'sport': {
            'running': Field('total_strides', FieldTypeBase(6), 'strides', None, None),  # base type: uint32
        },
    }),
    11: Field('total_calories', FieldTypeBase(4), 'kcal', None, None),  # base type: uint16
    13: Field('total_fat_calories', FieldTypeBase(4), 'kcal', None, None),  # base type: uint16
    14: Field('avg_speed', FieldTypeBase(4), 'm/s', 1000, None),  # base type: uint16
    15: Field('max_speed', FieldTypeBase(4), 'm/s', 1000, None),  # base type: uint16
    16: Field('avg_heart_rate', FieldTypeBase(2), 'bpm', None, None),  # base type: uint8
    17: Field('max_heart_rate', FieldTypeBase(2), 'bpm', None, None),  # base type: uint8
    18: DynamicField('avg_cadence', FieldTypeBase(2), 'rpm', None, None, {  # base type: uint8
        'sport': {
            'running': Field('avg_running_cadence', FieldTypeBase(2), 'strides/min', None, None),  # base type: uint8
        },
    }),
    19: DynamicField('max_cadence', FieldTypeBase(2), 'rpm', None, None, {  # base type: uint8
        'sport': {
            'running': Field('max_running_cadence', FieldTypeBase(2), 'strides/min', None, None),  # base type: uint8
        },
    }),
    20: Field('avg_power', FieldTypeBase(4), 'watts', None, None),  # base type: uint16
    21: Field('max_power', FieldTypeBase(4), 'watts', None, None),  # base type: uint16
    22: Field('total_ascent', FieldTypeBase(4), 'm', None, None),  # base type: uint16
    23: Field('total_descent', FieldTypeBase(4), 'm', None, None),  # base type: uint16
    24: Field('total_training_effect', FieldTypeBase(2), None, 10, None),  # base type: uint8
    25: Field('first_lap_index', FieldTypeBase(4), None, None, None),  # base type: uint16
    26: Field('num_laps', FieldTypeBase(4), None, None, None),  # base type: uint16
    27: Field('event_group', FieldTypeBase(2), None, None, None),  # base type: uint8
    28: Field('trigger', FieldType('session_trigger'), None, None, None),  # base type: enum
    29: Field('nec_lat', FieldTypeBase(5), 'semicircles', None, None),  # base type: sint32
    30: Field('nec_long', FieldTypeBase(5), 'semicircles', None, None),  # base type: sint32
    31: Field('swc_lat', FieldTypeBase(5), 'semicircles', None, None),  # base type: sint32
    32: Field('swc_long', FieldTypeBase(5), 'semicircles', None, None),  # base type: sint32
    253: Field('timestamp', FieldType('date_time'), 's', None, None),  # base type: uint32
    254: Field('message_index', FieldType('message_index'), None, None, None),  # base type: uint16
})

MessageType(19, 'lap', {
    0: Field('event', FieldType('event'), None, None, None),  # base type: enum
    1: Field('event_type', FieldType('event_type'), None, None, None),  # base type: enum
    2: Field('start_time', FieldType('date_time'), None, None, None),  # base type: uint32
    3: Field('start_position_lat', FieldTypeBase(5), 'semicircles', None, None),  # base type: sint32
    4: Field('start_position_long', FieldTypeBase(5), 'semicircles', None, None),  # base type: sint32
    5: Field('end_position_lat', FieldTypeBase(5), 'semicircles', None, None),  # base type: sint32
    6: Field('end_position_long', FieldTypeBase(5), 'semicircles', None, None),  # base type: sint32
    7: Field('total_elapsed_time', FieldTypeBase(6), 's', 1000, None),  # base type: uint32
    8: Field('total_timer_time', FieldTypeBase(6), 's', 1000, None),  # base type: uint32
    9: Field('total_distance', FieldTypeBase(6), 'm', 100, None),  # base type: uint32
    10: DynamicField('total_cycles', FieldTypeBase(6), 'cycles', None, None, {  # base type: uint32
        'sport': {
            'running': Field('total_strides', FieldTypeBase(6), 'strides', None, None),  # base type: uint32
        },
    }),
    11: Field('total_calories', FieldTypeBase(4), 'kcal', None, None),  # base type: uint16
    12: Field('total_fat_calories', FieldTypeBase(4), 'kcal', None, None),  # base type: uint16
    13: Field('avg_speed', FieldTypeBase(4), 'm/s', 1000, None),  # base type: uint16
    14: Field('max_speed', FieldTypeBase(4), 'm/s', 1000, None),  # base type: uint16
    15: Field('avg_heart_rate', FieldTypeBase(2), 'bpm', None, None),  # base type: uint8
    16: Field('max_heart_rate', FieldTypeBase(2), 'bpm', None, None),  # base type: uint8
    17: DynamicField('avg_cadence', FieldTypeBase(2), 'rpm', None, None, {  # base type: uint8
        'sport': {
            'running': Field('avg_running_cadence', FieldTypeBase(2), 'strides/min', None, None),  # base type: uint8
        },
    }),
    18: DynamicField('max_cadence', FieldTypeBase(2), 'rpm', None, None, {  # base type: uint8
        'sport': {
            'running': Field('max_running_cadence', FieldTypeBase(2), 'strides/min', None, None),  # base type: uint8
        },
    }),
    19: Field('avg_power', FieldTypeBase(4), 'watts', None, None),  # base type: uint16
    20: Field('max_power', FieldTypeBase(4), 'watts', None, None),  # base type: uint16
    21: Field('total_ascent', FieldTypeBase(4), 'm', None, None),  # base type: uint16
    22: Field('total_descent', FieldTypeBase(4), 'm', None, None),  # base type: uint16
    23: Field('intensity', FieldType('intensity'), None, None, None),  # base type: enum
    24: Field('lap_trigger', FieldType('lap_trigger'), None, None, None),  # base type: enum
    25: Field('sport', FieldType('sport'), None, None, None),  # base type: enum
    26: Field('event_group', FieldTypeBase(2), None, None, None),  # base type: uint8
    253: Field('timestamp', FieldType('date_time'), 's', None, None),  # base type: uint32
    254: Field('message_index', FieldType('message_index'), None, None, None),  # base type: uint16
})

MessageType(20, 'record', {
    0: Field('position_lat', FieldTypeBase(5), 'semicircles', None, None),  # base type: sint32
    1: Field('position_long', FieldTypeBase(5), 'semicircles', None, None),  # base type: sint32
    2: Field('altitude', FieldTypeBase(4), 'm', 5, 500),  # base type: uint16
    3: Field('heart_rate', FieldTypeBase(2), 'bpm', None, None),  # base type: uint8
    4: Field('cadence', FieldTypeBase(2), 'rpm', None, None),  # base type: uint8
    5: Field('distance', FieldTypeBase(6), 'm', 100, None),  # base type: uint32
    6: Field('speed', FieldTypeBase(4), 'm/s', 1000, None),  # base type: uint16
    7: Field('power', FieldTypeBase(4), 'watts', None, None),  # base type: uint16
    8: Field('compressed_speed_distance', FieldType('record-compressed_speed_distance'), 'm/s,\nm', None, None),  # base type: byte
    9: Field('grade', FieldTypeBase(3), '%', 100, None),  # base type: sint16
    10: Field('resistance', FieldTypeBase(2), None, None, None),  # base type: uint8
    11: Field('time_from_course', FieldTypeBase(5), 's', 1000, None),  # base type: sint32
    12: Field('cycle_length', FieldTypeBase(2), 'm', 100, None),  # base type: uint8
    13: Field('temperature', FieldTypeBase(1), 'C', None, None),  # base type: sint8
    253: Field('timestamp', FieldType('date_time'), 's', None, None),  # base type: uint32
})

MessageType(21, 'event', {
    0: Field('event', FieldType('event'), None, None, None),  # base type: enum
    1: Field('event_type', FieldType('event_type'), None, None, None),  # base type: enum
    2: DynamicField('data16', FieldTypeBase(4), None, None, None, {  # base type: uint16
        'event': {
            'cad_low_alert': Field('cad_low_alert', FieldTypeBase(4), 'rpm', None, None),  # base type: uint16
            'fitness_equipment': Field('fitness_equipment_state', FieldType('fitness_equipment_state'), None, None, None),  # base type: enum
            'calorie_duration_alert': Field('calorie_duration_alert', FieldTypeBase(6), 'calories', None, None),  # base type: uint32
            'cad_high_alert': Field('cad_high_alert', FieldTypeBase(4), 'rpm', None, None),  # base type: uint16
            'hr_high_alert': Field('hr_high_alert', FieldTypeBase(2), 'bpm', None, None),  # base type: uint8
            'battery': Field('battery_level', FieldTypeBase(4), 'V', 1000, None),  # base type: uint16
            'power_low_alert': Field('power_low_alert', FieldTypeBase(4), 'watts', None, None),  # base type: uint16
            'timer': Field('timer_trigger', FieldType('timer_trigger'), None, None, None),  # base type: enum
            'distance_duration_alert': Field('distance_duration_alert', FieldTypeBase(6), 'm', 100, None),  # base type: uint32
            'power_high_alert': Field('power_high_alert', FieldTypeBase(4), 'watts', None, None),  # base type: uint16
            'speed_low_alert': Field('speed_low_alert', FieldTypeBase(4), 'm/s', 1000, None),  # base type: uint16
            'time_duration_alert': Field('time_duration_alert', FieldTypeBase(6), 's', 1000, None),  # base type: uint32
            'virtual_partner_pace': Field('virtual_partner_speed', FieldTypeBase(4), 'm/s', 1000, None),  # base type: uint16
            'hr_low_alert': Field('hr_low_alert', FieldTypeBase(2), 'bpm', None, None),  # base type: uint8
            'speed_high_alert': Field('speed_high_alert', FieldTypeBase(4), 'm/s', 1000, None),  # base type: uint16
            'course_point': Field('course_point_index', FieldType('message_index'), None, None, None),  # base type: uint16
        },
    }),
    3: DynamicField('data', FieldTypeBase(6), None, None, None, {  # base type: uint32
        'event': {
            'cad_low_alert': Field('cad_low_alert', FieldTypeBase(4), 'rpm', None, None),  # base type: uint16
            'fitness_equipment': Field('fitness_equipment_state', FieldType('fitness_equipment_state'), None, None, None),  # base type: enum
            'calorie_duration_alert': Field('calorie_duration_alert', FieldTypeBase(6), 'calories', None, None),  # base type: uint32
            'cad_high_alert': Field('cad_high_alert', FieldTypeBase(4), 'rpm', None, None),  # base type: uint16
            'hr_high_alert': Field('hr_high_alert', FieldTypeBase(2), 'bpm', None, None),  # base type: uint8
            'battery': Field('battery_level', FieldTypeBase(4), 'V', 1000, None),  # base type: uint16
            'power_low_alert': Field('power_low_alert', FieldTypeBase(4), 'watts', None, None),  # base type: uint16
            'timer': Field('timer_trigger', FieldType('timer_trigger'), None, None, None),  # base type: enum
            'distance_duration_alert': Field('distance_duration_alert', FieldTypeBase(6), 'm', 100, None),  # base type: uint32
            'power_high_alert': Field('power_high_alert', FieldTypeBase(4), 'watts', None, None),  # base type: uint16
            'speed_low_alert': Field('speed_low_alert', FieldTypeBase(4), 'm/s', 1000, None),  # base type: uint16
            'time_duration_alert': Field('time_duration_alert', FieldTypeBase(6), 's', 1000, None),  # base type: uint32
            'virtual_partner_pace': Field('virtual_partner_speed', FieldTypeBase(4), 'm/s', 1000, None),  # base type: uint16
            'hr_low_alert': Field('hr_low_alert', FieldTypeBase(2), 'bpm', None, None),  # base type: uint8
            'speed_high_alert': Field('speed_high_alert', FieldTypeBase(4), 'm/s', 1000, None),  # base type: uint16
            'course_point': Field('course_point_index', FieldType('message_index'), None, None, None),  # base type: uint16
        },
    }),
    4: Field('event_group', FieldTypeBase(2), None, None, None),  # base type: uint8
    253: Field('timestamp', FieldType('date_time'), 's', None, None),  # base type: uint32
})

MessageType(23, 'device_info', {
    0: Field('device_index', FieldType('device_index'), None, None, None),  # base type: uint8
    1: Field('device_type', FieldType('device_type'), None, None, None),  # base type: uint8
    2: Field('manufacturer', FieldType('manufacturer'), None, None, None),  # base type: uint16
    3: Field('serial_number', FieldTypeBase(12), None, None, None),  # base type: uint32z
    4: Field('product', FieldTypeBase(4), None, None, None),  # base type: uint16
    5: Field('software_version', FieldTypeBase(4), None, 100, None),  # base type: uint16
    6: Field('hardware_version', FieldTypeBase(2), None, None, None),  # base type: uint8
    7: Field('cum_operating_time', FieldTypeBase(6), 's', None, None),  # base type: uint32
    10: Field('battery_voltage', FieldTypeBase(4), 'V', 256, None),  # base type: uint16
    11: Field('battery_status', FieldType('battery_status'), None, None, None),  # base type: uint8
    253: Field('timestamp', FieldType('date_time'), 's', None, None),  # base type: uint32
})

MessageType(26, 'workout', {
    4: Field('sport', FieldType('sport'), None, None, None),  # base type: enum
    5: Field('capabilities', FieldType('workout_capabilities'), None, None, None),  # base type: uint32z
    6: Field('num_valid_steps', FieldTypeBase(4), None, None, None),  # base type: uint16
    8: Field('wkt_name', FieldTypeBase(7), None, None, None),  # base type: string
})

MessageType(27, 'workout_step', {
    0: Field('wkt_step_name', FieldTypeBase(7), None, None, None),  # base type: string
    1: Field('duration_type', FieldType('wkt_step_duration'), None, None, None),  # base type: enum
    2: DynamicField('duration_value', FieldTypeBase(6), None, None, None, {  # base type: uint32
        'duration_type': {
            'repeat_until_power_less_than': Field('duration_step', FieldTypeBase(6), None, None, None),  # base type: uint32
            'distance': Field('duration_distance', FieldTypeBase(6), 'm', 100, None),  # base type: uint32
            'power_less_than': Field('duration_power', FieldType('workout_power'), '% or watts', None, None),  # base type: uint32
            'power_greater_than': Field('duration_power', FieldType('workout_power'), '% or watts', None, None),  # base type: uint32
            'repeat_until_power_greater_than': Field('duration_step', FieldTypeBase(6), None, None, None),  # base type: uint32
            'repeat_until_steps_cmplt': Field('duration_step', FieldTypeBase(6), None, None, None),  # base type: uint32
            'hr_less_than': Field('duration_hr', FieldType('workout_hr'), '% or bpm', None, None),  # base type: uint32
            'calories': Field('duration_calories', FieldTypeBase(6), 'calories', None, None),  # base type: uint32
            'repeat_until_time': Field('duration_step', FieldTypeBase(6), None, None, None),  # base type: uint32
            'hr_greater_than': Field('duration_hr', FieldType('workout_hr'), '% or bpm', None, None),  # base type: uint32
            'repeat_until_distance': Field('duration_step', FieldTypeBase(6), None, None, None),  # base type: uint32
            'repeat_until_calories': Field('duration_step', FieldTypeBase(6), None, None, None),  # base type: uint32
            'time': Field('duration_time', FieldTypeBase(6), 's', 1000, None),  # base type: uint32
            'repeat_until_hr_greater_than': Field('duration_step', FieldTypeBase(6), None, None, None),  # base type: uint32
            'repeat_until_hr_less_than': Field('duration_step', FieldTypeBase(6), None, None, None),  # base type: uint32
        },
    }),
    3: Field('target_type', FieldType('wkt_step_target'), None, None, None),  # base type: enum
    4: DynamicField('target_value', FieldTypeBase(6), None, None, None, {  # base type: uint32
        'duration_type': {
            'repeat_until_power_less_than': Field('repeat_power', FieldType('workout_power'), '% or watts', None, None),  # base type: uint32
            'repeat_until_steps_cmplt': Field('repeat_steps', FieldTypeBase(6), None, None, None),  # base type: uint32
            'repeat_until_power_greater_than': Field('repeat_power', FieldType('workout_power'), '% or watts', None, None),  # base type: uint32
            'repeat_until_time': Field('repeat_time', FieldTypeBase(6), 's', 1000, None),  # base type: uint32
            'repeat_until_calories': Field('repeat_calories', FieldTypeBase(6), 'calories', None, None),  # base type: uint32
            'repeat_until_distance': Field('repeat_distance', FieldTypeBase(6), 'm', 100, None),  # base type: uint32
            'repeat_until_hr_greater_than': Field('repeat_hr', FieldType('workout_hr'), '% or bpm', None, None),  # base type: uint32
            'repeat_until_hr_less_than': Field('repeat_hr', FieldType('workout_hr'), '% or bpm', None, None),  # base type: uint32
        },
        'target_type': {
            'heart_rate': Field('target_hr_zone', FieldTypeBase(6), None, None, None),  # base type: uint32
            'power': Field('target_power_zone', FieldTypeBase(6), None, None, None),  # base type: uint32
        },
    }),
    5: DynamicField('custom_target_value_low', FieldTypeBase(6), None, None, None, {  # base type: uint32
        'target_type': {
            'heart_rate': Field('custom_target_heart_rate_low', FieldType('workout_hr'), '% or bpm', None, None),  # base type: uint32
            'speed': Field('custom_target_speed_low', FieldTypeBase(6), 'm/s', 1000, None),  # base type: uint32
            'power': Field('custom_target_power_low', FieldType('workout_power'), '% or watts', None, None),  # base type: uint32
            'cadence': Field('custom_target_cadence_low', FieldTypeBase(6), 'rpm', None, None),  # base type: uint32
        },
    }),
    6: DynamicField('custom_target_value_high', FieldTypeBase(6), None, None, None, {  # base type: uint32
        'target_type': {
            'heart_rate': Field('custom_target_heart_rate_high', FieldType('workout_hr'), '% or bpm', None, None),  # base type: uint32
            'speed': Field('custom_target_speed_high', FieldTypeBase(6), 'm/s', 1000, None),  # base type: uint32
            'power': Field('custom_target_power_high', FieldType('workout_power'), '% or watts', None, None),  # base type: uint32
            'cadence': Field('custom_target_cadence_high', FieldTypeBase(6), 'rpm', None, None),  # base type: uint32
        },
    }),
    7: Field('intensity', FieldType('intensity'), None, None, None),  # base type: enum
    254: Field('message_index', FieldType('message_index'), None, None, None),  # base type: uint16
})

MessageType(30, 'weight_scale', {
    0: Field('weight', FieldType('weight'), 'kg', 100, None),  # base type: uint16
    1: Field('percent_fat', FieldTypeBase(4), '%', 100, None),  # base type: uint16
    2: Field('percent_hydration', FieldTypeBase(4), '%', 100, None),  # base type: uint16
    3: Field('visceral_fat_mass', FieldTypeBase(4), 'kg', 100, None),  # base type: uint16
    4: Field('bone_mass', FieldTypeBase(4), 'kg', 100, None),  # base type: uint16
    5: Field('muscle_mass', FieldTypeBase(4), 'kg', 100, None),  # base type: uint16
    7: Field('basal_met', FieldTypeBase(4), 'kcal/day', 4, None),  # base type: uint16
    8: Field('physique_rating', FieldTypeBase(2), None, None, None),  # base type: uint8
    9: Field('active_met', FieldTypeBase(4), 'kcal/day', 4, None),  # base type: uint16
    10: Field('metabolic_age', FieldTypeBase(2), 'years', None, None),  # base type: uint8
    11: Field('visceral_fat_rating', FieldTypeBase(2), None, None, None),  # base type: uint8
    12: Field('user_profile_index', FieldType('message_index'), None, None, None),  # base type: uint16
    253: Field('timestamp', FieldType('date_time'), 's', None, None),  # base type: uint32
})

MessageType(31, 'course', {
    4: Field('sport', FieldType('sport'), None, None, None),  # base type: enum
    5: Field('name', FieldTypeBase(7), None, None, None),  # base type: string
    6: Field('capabilities', FieldType('course_capabilities'), None, None, None),  # base type: uint32z
})

MessageType(32, 'course_point', {
    1: Field('timestamp', FieldType('date_time'), None, None, None),  # base type: uint32
    2: Field('position_lat', FieldTypeBase(5), 'semicircles', None, None),  # base type: sint32
    3: Field('position_long', FieldTypeBase(5), 'semicircles', None, None),  # base type: sint32
    4: Field('distance', FieldTypeBase(6), 'm', 100, None),  # base type: uint32
    5: Field('type', FieldType('course_point'), None, None, None),  # base type: enum
    6: Field('name', FieldTypeBase(7), None, None, None),  # base type: string
    254: Field('message_index', FieldType('message_index'), None, None, None),  # base type: uint16
})

MessageType(33, 'totals', {
    0: Field('timer_time', FieldTypeBase(6), 's', None, None),  # base type: uint32
    1: Field('distance', FieldTypeBase(6), 'm', None, None),  # base type: uint32
    2: Field('calories', FieldTypeBase(6), 'kcal', None, None),  # base type: uint32
    3: Field('sport', FieldType('sport'), None, None, None),  # base type: enum
    4: Field('elapsed_time', FieldTypeBase(6), 's', None, None),  # base type: uint32
    253: Field('timestamp', FieldType('date_time'), 's', None, None),  # base type: uint32
    254: Field('message_index', FieldType('message_index'), None, None, None),  # base type: uint16
})

MessageType(34, 'activity', {
    0: Field('total_timer_time', FieldTypeBase(6), 's', 1000, None),  # base type: uint32
    1: Field('num_sessions', FieldTypeBase(4), None, None, None),  # base type: uint16
    2: Field('type', FieldType('activity'), None, None, None),  # base type: enum
    3: Field('event', FieldType('event'), None, None, None),  # base type: enum
    4: Field('event_type', FieldType('event_type'), None, None, None),  # base type: enum
    5: Field('local_timestamp', FieldType('date_time'), None, None, None),  # base type: uint32
    6: Field('event_group', FieldTypeBase(2), None, None, None),  # base type: uint8
    253: Field('timestamp', FieldType('date_time'), None, None, None),  # base type: uint32
})

MessageType(35, 'software', {
    3: Field('version', FieldTypeBase(4), None, 100, None),  # base type: uint16
    5: Field('part_number', FieldTypeBase(7), None, None, None),  # base type: string
    254: Field('message_index', FieldType('message_index'), None, None, None),  # base type: uint16
})

MessageType(37, 'file_capabilities', {
    0: Field('type', FieldType('file'), None, None, None),  # base type: enum
    1: Field('flags', FieldType('file_flags'), None, None, None),  # base type: uint8z
    2: Field('directory', FieldTypeBase(7), None, None, None),  # base type: string
    3: Field('max_count', FieldTypeBase(4), None, None, None),  # base type: uint16
    4: Field('max_size', FieldTypeBase(6), 'bytes', None, None),  # base type: uint32
    254: Field('message_index', FieldType('message_index'), None, None, None),  # base type: uint16
})

MessageType(38, 'mesg_capabilities', {
    0: Field('file', FieldType('file'), None, None, None),  # base type: enum
    1: Field('mesg_num', FieldType('mesg_num'), None, None, None),  # base type: uint16
    2: Field('count_type', FieldType('mesg_count'), None, None, None),  # base type: enum
    3: DynamicField('count', FieldTypeBase(4), None, None, None, {  # base type: uint16
        'count_type': {
            'num_per_file': Field('num_per_file', FieldTypeBase(4), None, None, None),  # base type: uint16
            'max_per_file_type': Field('max_per_file_type', FieldTypeBase(4), None, None, None),  # base type: uint16
            'max_per_file': Field('max_per_file', FieldTypeBase(4), None, None, None),  # base type: uint16
        },
    }),
    254: Field('message_index', FieldType('message_index'), None, None, None),  # base type: uint16
})

MessageType(39, 'field_capabilities', {
    0: Field('file', FieldType('file'), None, None, None),  # base type: enum
    1: Field('mesg_num', FieldType('mesg_num'), None, None, None),  # base type: uint16
    2: Field('field_num', FieldTypeBase(2), None, None, None),  # base type: uint8
    3: Field('count', FieldTypeBase(4), None, None, None),  # base type: uint16
    254: Field('message_index', FieldType('message_index'), None, None, None),  # base type: uint16
})

MessageType(49, 'file_creator', {
    0: Field('software_version', FieldTypeBase(4), None, None, None),  # base type: uint16
    1: Field('hardware_version', FieldTypeBase(2), None, None, None),  # base type: uint8
})

MessageType(51, 'blood_pressure', {
    0: Field('systolic_pressure', FieldTypeBase(4), 'mmHg', None, None),  # base type: uint16
    1: Field('diastolic_pressure', FieldTypeBase(4), 'mmHg', None, None),  # base type: uint16
    2: Field('mean_arterial_pressure', FieldTypeBase(4), 'mmHg', None, None),  # base type: uint16
    3: Field('map_3_sample_mean', FieldTypeBase(4), 'mmHg', None, None),  # base type: uint16
    4: Field('map_morning_values', FieldTypeBase(4), 'mmHg', None, None),  # base type: uint16
    5: Field('map_evening_values', FieldTypeBase(4), 'mmHg', None, None),  # base type: uint16
    6: Field('heart_rate', FieldTypeBase(2), 'bpm', None, None),  # base type: uint8
    7: Field('heart_rate_type', FieldType('hr_type'), None, None, None),  # base type: enum
    8: Field('status', FieldType('bp_status'), None, None, None),  # base type: enum
    9: Field('user_profile_index', FieldType('message_index'), None, None, None),  # base type: uint16
    253: Field('timestamp', FieldType('date_time'), 's', None, None),  # base type: uint32
})


######################   DELETE CONVERSION FUNCTIONS   #######################

del _convert_activity_class
del _convert_bool
del _convert_date_time
del _convert_local_date_time
del _convert_message_index
del _convert_record_compressed_speed_distance


########################   AUTOGENERATION COMPLETE   #########################
