const localVideo = document.getElementById('video_client');
const serverVideo = document.getElementById('video_server');
// const ws = new WebSocket("ws://localhost:8000/offer");

let localStream

async function start() {
    const stream = await navigator.mediaDevices.getUserMedia({video: true})
    localVideo.srcObject = stream
    localStream = stream
}

async function call() {
    let pc = new RTCPeerConnection({});
    pc.addEventListener('track', (evt) => {
        console.log('track', evt)
        if(serverVideo.srcObject !== evt.streams[0]){
            serverVideo.srcObject = evt.streams[0]
        }
    })
    localStream.getTracks().forEach((track) => pc.addTrack(track));
    const offer= await pc.createOffer({offerToReceiveAudio: true, offerToReceiveVideo: true})
    await pc.setLocalDescription(offer);
    const iceGathering = async() => {
        return new Promise(function(resolve) {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                function checkState() {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                }
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }
    await iceGathering();
    const answerReq = await fetch("http://localhost:8000/offer", {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(offer)
    })
    const answer = await answerReq.json()
    await pc.setRemoteDescription(answer)

}
// let pc = new RTCPeerConnection({});
    // pc.addEventListener("icecandidate", (evt) => {
    //     if(evt.candidate !== null) {
    //         ws.send(JSON.stringify({type: "icecandidate", data: evt.candidate}));
    //     }
    // })
    // let offer = await pc.createOffer({offerToReceiveVideo: true, offerToReceiveAudio: true});
    // await pc.setLocalDescription(offer);
    // ws.send(JSON.stringify({type: "offer", data: offer}));
    // ws.addEventListener("message", (message) => {
    //     let data = JSON.parse(message.data)
    //     switch (data.type) {
    //         case 'answer':
    //             pc.setRemoteDescription(data.data)
    //             break;
    //         case 'ice':
    //     }
    // })