import React from 'react';
import ReactDOM from 'react-dom';
import { enquireScreen } from 'enquire-js';
import './styles/index.less';
import Home from './Home';
import * as serviceWorker from './serviceWorker';

let isMobile = false;
enquireScreen(b => {
  isMobile = b;
});

ReactDOM.render(<Home isMobile={isMobile} />, document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
