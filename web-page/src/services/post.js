import axios from 'axios';

export function getTargets() {
    return axios.get('http://34.82.172.56/targets');
}
