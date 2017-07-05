(winddirection,convolution,minspeed,sortkey,rev)=(90,10,3.5,"min speed",True)
(winddirection,convolution,minspeed,sortkey,rev)=WxQuery("Jibe detection parameters",    \
                [('wxentry','Wind Direction',None,winddirection,'float','in degrees, North id 0, West is 90, South 180'),\
                ('wxentry','convolution',None,convolution,'int','nuumber of points to use for data smoothing'),\
                ('wxentry','Minimal speed',None,minspeed,'float','ignore any jibe when convolved speed is below this value'),\
                ('wxcombo','Sort by','Time|TimeStamp|min speed|max speed',sortkey,'str'),\
                ('wxcheck','Desc',None,rev,'bool')]
                )
if not 'conv_speed' in gpx.get_header_names(): gpx.append_column('conv_speed','float')
if not 'tack' in gpx.get_header_names():       gpx.append_column('tack','float')
gpx.set_unit('conv_speed','kts')
gpx['conv_speed']=np.convolve(gpx[('speed',1)], np.ones(convolution)/convolution,mode='same')
gpx['tack']=np.sin(np.radians(gpx['course']-winddirection))

jibes=[]
zerocrossing=np.where(np.diff(np.sign(gpx['tack'])))[0]
for t in zerocrossing[1:]:
    if (t>convolution)   and  ( (gpx[('conv_speed',1)][t-convolution:t+convolution]>=minspeed).all()):
        jibes.append( (t,
                        gpx['time'][t],
                        np.min(gpx[('speed',1)][t-convolution:t+convolution]),
                        np.max(gpx[('speed',1)][t-convolution:t+convolution]),
                        dist2pt(t-convolution,t+convolution)*(np.cos(course2pt(t-convolution,t+convolution)-winddirirection))
                        
                        ) )
sortnum='Time|TimeStamp|min speed|max speed'.split('|').index(sortkey)
print "Time (s), Timestamp, Min Speed, Max Speed"
for j in sorted(jibes,key=lambda tup: tup[sortnum],reverse=rev):
    print j
