import axios from 'axios';

export function getTargets() {
    return axios.get('http://34.82.172.56/targets');
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
    return axios.post('http://34.82.172.56/process',form);
}

export function postTarget(targetImage){
    let form = new FormData()
    form.append('image',targetImage)
    return axios.post('http://34.82.172.56/targets',form)

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
    return axios.post('http://34.82.172.56/live', form);
}