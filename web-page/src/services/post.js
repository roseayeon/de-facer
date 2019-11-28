import axios from 'axios';

export function getTargets() {
    return axios.get('http://34.82.172.56/targets');
    // return axios.get('http://143.248.217.16/targets');
}
export function postProcess(targetUrls, videoFile) {
    let form = new FormData()
    form.append('targets',targetUrls)
    form.append('video',videoFile)
    return axios.post('http://34.82.172.56/process',form);
}

export function postTarget(targetImage){
    let form = new FormData()
    form.append('image',targetImage)
    return axios.post('http://34.82.172.56/targets',form)

}