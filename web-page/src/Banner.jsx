import React from 'react';
import TweenOne from 'rc-tween-one';
import QueueAnim from 'rc-queue-anim';
import ScrollParallax from 'rc-scroll-anim/lib/ScrollParallax';
import classNames from 'classnames';
import BannerImage from './BannerImage';
import './styles/common.scss';

const loop = {
  duration: 3000,
  yoyo: true,
  repeat: -1,
};

const Banner = ({ isMobile }) => {
  return (
    <div className={classNames('homePageWrapper', 'bannerWrapper')} id="banner">
      <div className="bannerBgWrapper">
        <svg width="400px" height="576px" viewBox="0 0 400 576" fill="none">
          <TweenOne component="g" animation={[{ opacity: 0, type: 'from' }, { ...loop, y: 15 }]}>
            <ellipse cx="100" cy="100" rx="6" ry="6" stroke="#2F54EB" strokeWidth="1.6" />
          </TweenOne>
          <TweenOne component="g" animation={[{ opacity: 0, type: 'from' }, { ...loop, y: -15 }]}>
            <g transform="translate(200 450)">
              <g style={{ transformOrigin: '50% 50%', transform: 'rotate(-340deg)' }}>
                <rect stroke="#FADB14" strokeWidth="1.6" width="9" height="9" />
              </g>
            </g>
          </TweenOne>
        </svg>
        <ScrollParallax
          location="banner"
          className="bannerBg"
          animation={{ playScale: [1, 1.5], rotate: 0 }}
        />
      </div>
      <QueueAnim className="banner page" type="alpha" delay={150}>
        {isMobile && (
          <div className="imgWrapper" key="image">
            <BannerImage />
          </div>
        )}
        <QueueAnim className="textWrapper" key="text" type="bottom">
          <h1 key="h1">De-facer</h1>
          <p> <b>De-facer</b> is a tool that protects portrait-rights of faces which are <b>not targeted</b> from the given video. You can <b>blur</b> or <b>cover faces with other images</b>. Even real-time works! 😉 </p>
          <div
            key="promote"
            className="bannerPromote"
            style={{
              width: 522,
            }}
          >
          </div>
        </QueueAnim>
        {!isMobile && (
          <div className="imgWrapper" key="image">
            <ScrollParallax
              location="banner"
              component={BannerImage}
              animation={{ playScale: [1, 1.5], y: 80 }}
            />
          </div>
        )}
      </QueueAnim>
    </div>
  );
};

export default Banner;
