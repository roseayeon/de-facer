import React from 'react';
import RcFooter from 'rc-footer';
import 'rc-footer/assets/index.css';

class Footer extends React.Component {

  render() {
    return (
      <RcFooter
        bottom={
          <>
            CS470 Team 13 
          </>
        }
      />
    );
  }
}
export default Footer;
