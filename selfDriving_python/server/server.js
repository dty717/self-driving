const net = require('net');
const fs = require('fs');

var index = 0;
var list = ["Hello", "my job", "go"]

// var isRecording = false
// var recordingStr = ""
// var lastRecording = false
// var lastRecordingLength = 0

isRecording = false
recordingStr = ""
lastRecording = false
lastRecordingLength = 0

var dataLen = 1200
var lastDataFrame = 1192

var flieLocation = 'C:/Users/18751/Desktop/github/dty717/self-driving/selfDriving_python/file/'

function createFile(data) {
  data = 'a=`' + data + '`'
  var dateStr = new Date().toISOString().replace(/T/, ' ').replace(/\..+/, '').replace(/[-\s:]/g, '_')
  fs.writeFile(flieLocation + dateStr + '.js', data, (err) => {
    if (err) throw err;
    console.log('The file has been saved!');
  });
}

const server = net.createServer((c) => {
  // 'connection' listener.
  console.log('client connected:' + c.remoteAddress);
  //console.log(c);
  //console.log(c.address());
  // var p = index++%3;
  // var timer = setInterval(function(e){
  //   var content = "##0098QN=20210406134949;ST=21;CN=1062;PW=123456;MN=012345678901234567890123;Flag=5;CP=&&RtdInterval=40&&00BF\r\n"
  //   console.log("send")
  //   c.write(content);
  // },10000)
  _c = c;
  c.on('data', (e) => {
    try {
      if (new String(e).match(/^#\d+:/)) {
        splitIndex = e.indexOf(':')
        if (new String(e.subarray(1, splitIndex)) == '1') {
          if (!isRecording) {
            isRecording = true
            recordingStr = ""
            console.log("recording image")
            recordingStr = e.subarray(splitIndex + 1).join(',')
            console.log(new String(e.subarray(1, splitIndex + 1) + new Array(...e.subarray(splitIndex + 1)).map(e => e > 0xf ? e.toString(16) : ('0' + e.toString(16))).join('')))
          } else {
            recordingStr += ',' + e.subarray(splitIndex + 1).join(',')
            console.log(new String(new Array(...e).map(e => e > 0xf ? e.toString(16) : ('0' + e.toString(16))).join('')))
          }
        } else if (new String(e.subarray(1, splitIndex)) == '' + lastDataFrame) {
          console.log(new String(e.subarray(1, splitIndex + 1) + new Array(...e.subarray(splitIndex + 1)).map(e => e > 0xf ? e.toString(16) : ('0' + e.toString(16))).join('')))
          if (e.length < dataLen + '#' + lastDataFrame + ':'.length) {
            recordingStr += ',' + e.subarray(splitIndex + 1).join(',')
            lastRecording = true
            lastRecordingLength = e.length
          } else {
            recordingStr += ',' + e.subarray(splitIndex + 1, (splitIndex + 1) + dataLen).join(',')
            var recordingStrList = recordingStr.split(',')
            console.log('final result1')
            var recordingFileContent = ''
            for (let index = 0; index < recordingStrList.length; index += 2) {
              if (index + 2 > recordingStrList.length) {
                const element = (parseInt(recordingStrList[index]) << 8);
                recordingFileContent += element
              } else if (index + 2 == recordingStrList.length) {
                const element = (parseInt(recordingStrList[index]) << 8) + parseInt(recordingStrList[index + 1]);
                recordingFileContent += element
              } else {
                const element = (parseInt(recordingStrList[index]) << 8) + parseInt(recordingStrList[index + 1]);
                recordingFileContent += element + "\n"
              }
            }
            // console.log(recordingStr)
            createFile(recordingFileContent)
            isRecording = false
            recordingStr = ""
          }
        } else {
          recordingStr += ',' + e.subarray(splitIndex + 1).join(',')
          console.log(new String(e.subarray(1, splitIndex + 1) + new Array(...e.subarray(splitIndex + 1)).map(e => e > 0xf ? e.toString(16) : ('0' + e.toString(16))).join('')))
        }
      }
      else if (new String(e).match(/\d+-\d+-\d+ \d+:\d+:\d+ active:/)) {
        console.log(new String(e))
      }
      else {
        if (isRecording) {
          if (lastRecording) {
            lastRecordingLength += e.length
            if (lastRecordingLength < dataLen) {
              recordingStr += ',' + e.subarray(splitIndex + 1).join(',')
            } else {
              recordingStr += ',' + e.subarray(splitIndex + 1, (splitIndex + 1) + dataLen - lastRecordingLength).join(',')
              console.log('final result2')
              var recordingStrList = recordingStr.split(',')
              var recordingFileContent = ''
              for (let index = 0; index < recordingStrList.length; index += 2) {
                if (index + 2 > recordingStrList.length) {
                  const element = (parseInt(recordingStrList[index]) << 8);
                  recordingFileContent += element
                } else if (index + 2 == recordingStrList.length) {
                  const element = (parseInt(recordingStrList[index]) << 8) + parseInt(recordingStrList[index + 1]);
                  recordingFileContent += element
                } else {
                  const element = (parseInt(recordingStrList[index]) << 8) + parseInt(recordingStrList[index + 1]);
                  recordingFileContent += element + "\n"
                }
              }
              createFile(recordingFileContent)
              lastRecording = false
              isRecording = false
              recordingStr = ""
              lastRecordingLength = 0
            }
          } else {
            recordingStr += ',' + e.subarray(splitIndex + 1).join(',')
          }
          console.log(new String(new Array(...e).map(e => e > 0xf ? e.toString(16) : ('0' + e.toString(16))).join('')))
        } else {
          console.log(new String(e))
        }
      }
      //   128
    } catch (error) {
      console.log(e);
    }
  });
  c.on('end', () => {
    // clearInterval(timer);
    console.log('client disconnected');
  });
  // c.write('hello\r\n');
  //c.pipe(c);
});
server.on('error', (err) => {
  throw err;
});
//server.address("127.0.0.1")
server.listen(8808, () => {
  console.log('server bound');
});
