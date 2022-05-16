import festival
import sys,shutil,os
import subprocess

txtFile="".join(sys.argv[1])#.encode('iso8859-15',"replace")
with open(txtFile,"r") as f:
	txt=f.read()


confDir=os.path.join(os.environ.get('HOME','/tmp'),".config/accesshelper")
stretch=float(sys.argv[2])
voice=sys.argv[3]
currentDate=sys.argv[4]

p=subprocess.Popen(["festival"],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
p.stdin.write("(voice_{})\n".format(voice).encode("utf8"))
p.stdin.write("(Parameter.set 'Duration_Stretch {})\n".format(stretch).encode("utf8"))
p.stdin.write("(set! utt (Utterance Text {}))\n".format(txt).encode("iso8859-1"))
p.stdin.write("(utt.synth utt)\n".encode("utf8"))
p.stdin.write("(utt.save.wave utt \"/tmp/.myutt.wav\" \'riff)\n".encode("utf8"))
p.communicate()
print(p)
mp3Dir=os.path.join(confDir,"tts/mp3")
mp3File=os.path.join(mp3Dir,"{}.mp3".format(currentDate))
p=subprocess.run(["lame","/tmp/.myutt.wav",mp3File],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
os.unlink("/tmp/.myutt.wav")
#p.terminate()
player=False
if player==True:
	#self._debug("Playing {} with vlc".format(mp3))
	subprocess.run(["vlc",mp3File])
else:
	#self._debug("Playing {} with TTS Strech {}".format(mp3,self.stretch))
	subprocess.run(["play",mp3File])

### exit
sys.exit(0)
festival.execCommand("({})".format(voice))
festival.setStretchFactor(stretch)
mp3=festival.textToMp3File(txt)
mp3File="{}.mp3".format(currentDate)
shutil.move(mp3,os.path.join(mp3Dir,mp3File))
mp3=os.path.join(mp3Dir,mp3File)
