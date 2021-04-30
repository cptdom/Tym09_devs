import axios from 'axios';

const instance = axios.create({
    baseURL: 'https://testwebapp-3ab8b-default-rtdb.europe-west1.firebasedatabase.app'
})


export default instance;