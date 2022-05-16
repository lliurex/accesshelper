import sys,shutil,os
import subprocess

txtFile="".join(sys.argv[1])#.encode('iso8859-15',"replace")
with open(txtFile,"r") as f:
	txt=f.read()


confDir=os.path.join(os.environ.get('HOME','/tmp'),".config/accesshelper")
stretch=float(sys.argv[2])
voice=sys.argv[3]
currentDate=sys.argv[4]
player=sys.argv[5]
if player=="vlc":
	player=True
else:
	player=False

p=subprocess.Popen(["festival","--pipe"],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
if voice.startswith("voice_")==False:
	voice="voice_{}".format(voice)
p.stdin.write("({})\n".format(voice).encode("utf8"))
p.stdin.write("(Parameter.set 'Duration_Stretch {})\n".format(stretch).encode("utf8"))
p.stdin.write("(set! utt (Utterance Text {}))\n".format(txt).encode("iso8859-1"))
p.stdin.write("(utt.synth utt)\n".encode("utf8"))
p.stdin.write("(utt.save.wave utt \"/tmp/.myutt.wav\" \'riff)\n".encode("utf8"))
p.communicate()
mp3Dir=os.path.join(confDir,"tts/mp3")
mp3File=os.path.join(mp3Dir,"{}.mp3".format(currentDate))
p=subprocess.run(["lame","/tmp/.myutt.wav",mp3File],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
os.unlink("/tmp/.myutt.wav")
if player==True:
	#self._debug("Playing {} with vlc".format(mp3))
	subprocess.run(["vlc",mp3File])
else:
	#self._debug("Playing {} with TTS Strech {}".format(mp3,self.stretch))
	subprocess.run(["play",mp3File])

### exit
sys.exit(0)
