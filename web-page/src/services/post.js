import axios from 'axios';

const ip = window.location.hostname;
export function getTargets() {
    return axios.get('http://'+ip+'/targets');
}
export function postProcess(targetUrls, videoFile, replacement = []) {
    let form = new FormData()
    form.append('targets',JSON.stringify(targetUrls))
    form.append('video',videoFile)
    console.log(targetUrls)
    console.log(videoFile)
    if (replacement.length !== 0) {
        form.append('replacement',replacement[0].originFileObj)
        console.log(replacement[0].originFileObj)
    } else {
        console.log('replacement is empty')
    }
    return axios.post('http://'+ip+'/process',form);
}

export function postTarget(targetImage){
    let form = new FormData()
    form.append('image',targetImage)
    return axios.post('http://'+ip+'/targets',form)

}

export function postRealTime(targetUrls, videoUrl, replacement = []) {
    let form = new FormData()
    form.append('targets',JSON.stringify(targetUrls))
    form.append('url',videoUrl)
    console.log(targetUrls)
    console.log(videoUrl)
    if (replacement.length !== 0) {
        form.append('replacement',replacement[0].originFileObj)
        console.log(replacement[0].originFileObj)
    } else {
        console.log('replacement is empty')
    }
    return axios.post('http://'+ip+'/live', form);
}