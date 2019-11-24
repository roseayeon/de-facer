import React from 'react';
import PropTypes from 'prop-types';
import Banner from './Banner';
import Page1 from './Page1';
import Page2 from './Page2';
// import Page3 from './Page3';
import Footer from './Footer';
import 'antd/dist/antd.css';
import './styles/common.scss';

function getStyle() {
  return `
    .main-wrapper {
      padding: 0;
    }
    #header {
      box-shadow: none;
      max-width: 1200px;
      width: 100%;
      margin: 20px auto 0;
      padding: 0 24px;
    }
    #header,
    #header .ant-select-selection,
    #header .ant-menu {
      background: transparent;
    }
    #header #logo {
      padding: 0;
    }
    #header #nav .ant-menu-item {
      border-color: transparent;
    }
    #header #nav .ant-menu-submenu {
      border-color: transparent;
    }
    #header #nav .ant-menu-item.hide-in-home-page {
      display: none;
    }
    #header .ant-row > div:last-child .header-lang-button {
      margin-right: 0;
    }
    .rc-footer-container {
      max-width: 1200px;
      padding: 80px 0;
    }

    .rc-footer-bottom-container {
      max-width: 1200px;
    }

    .rc-footer-columns {
      justify-content: space-around;
    }
  `;
}
// eslint-disable-next-line react/prefer-stateless-function
class Home extends React.Component {
  static contextTypes = {
    isMobile: PropTypes.bool.isRequired,
  };

  render() {
    const { isMobile } = this.context;
    const childProps = { ...this.props, isMobile, };
    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: getStyle() }} /> {/* eslint-disable-line */}
          <title>{`De-facer`}</title>
        <Banner {...childProps} />
        <Page1 {...childProps} />
        <Page2 {...childProps} />
        <Footer />
      </>
    );
  }
}

export default Home;
