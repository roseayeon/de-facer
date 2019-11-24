import React from 'react';
import { Upload, Button, Icon, message, Radio, Steps } from 'antd';
import ScrollParallax from 'rc-scroll-anim/lib/ScrollParallax';
import 'antd/dist/antd.css';

import * as service from './services/post';
import './styles/common.scss';

function ParallaxG(props) {
  return <ScrollParallax component="g" {...props} />;
}

function svgBgToParallax(children, i = 0) {
    const svgChildren = React.Children.toArray(children).map((child, ii) => (
      <ParallaxG
        key={ii.toString()}
        location="page1"
        animation={{
          y: Math.random() * -200 - 30 - i * 20,
          playScale: [0, Math.random() + 2],
        }}
      >
        {child}
      </ParallaxG>
    ));
    return svgChildren;
  }

const svgBg = [
  <circle stroke="#13C2C2" cx="530" cy="195" r="5" key="13C2C2-530-195" />,
  <circle fillOpacity="0.4" fill="#9EE6E6" cx="606" cy="76" r="3" key="9EE6E6-606-76" />,
  <circle stroke="#13C2C2" cx="165" cy="540" r="5" key="13C2C2-165-540" />,
  <circle stroke="#CED4D9" cx="701.5" cy="650" r="3.5" key="CED4D9-701-650" />,
  <circle stroke="#F5222D" cx="526.5" cy="381.5" r="3.5" key="F5222D-526-381" />,
  <circle fillOpacity="0.4" fill="#9EE6E6" cx="944" cy="251" r="5" key="9EE6E6-944-251" />,
  <g transform="translate(0, 180)" key="g-180">
    <path
      d="M1182.79367,448.230356 L1186.00213,453.787581 C1186.55442,454.744166 1186.22667,455.967347 1185.27008,456.519632 C1184.96604,456.695168 1184.62116,456.787581 1184.27008,456.787581 L1177.85315,456.787581 C1176.74858,456.787581 1175.85315,455.89215 1175.85315,454.787581 C1175.85315,454.436507 1175.94556,454.091619 1176.1211,453.787581 L1179.32957,448.230356 C1179.88185,447.273771 1181.10503,446.946021 1182.06162,447.498305 C1182.36566,447.673842 1182.61813,447.926318 1182.79367,448.230356 Z"
      stroke="#CED4D9"
      transform="translate(1181.061784, 452.008801) rotate(40.000000) translate(-1181.061784, -452.008801) "
    />
  </g>,
  <g transform="translate(0, 100)" key="g-100">
    <path
      d="M1376.79367,204.230356 L1380.00213,209.787581 C1380.55442,210.744166 1380.22667,211.967347 1379.27008,212.519632 C1378.96604,212.695168 1378.62116,212.787581 1378.27008,212.787581 L1371.85315,212.787581 C1370.74858,212.787581 1369.85315,211.89215 1369.85315,210.787581 C1369.85315,210.436507 1369.94556,210.091619 1370.1211,209.787581 L1373.32957,204.230356 C1373.88185,203.273771 1375.10503,202.946021 1376.06162,203.498305 C1376.36566,203.673842 1376.61813,203.926318 1376.79367,204.230356 Z"
      stroke="#2F54EB"
      transform="translate(1375.061784, 208.008801) rotate(40.000000) translate(-1375.061784, -208.008801) "
    />
  </g>,
  <rect
    key="1D39C4-942-222"
    strokeOpacity="0.4"
    stroke="#1D39C4"
    transform="translate(949.801502, 129.801502) rotate(30.000000) translate(-949.801502, -129.801502) "
    x="942.626304"
    y="222.626304"
    width="14.3503946"
    height="14.3503946"
    rx="1"
  />,
  <rect
    key="CED4D9-107-254"
    stroke="#CED4D9"
    transform="translate(111.673081, 158.673081) rotate(30.000000) translate(-111.673081, -158.673081) "
    x="107.288047"
    y="254.288047"
    width="8.77006914"
    height="8.77006914"
    rx="1"
  />,
];
const svgChildren = svgBgToParallax(svgBg);
const { Dragger } = Upload;

class Page2 extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            fileList: [],
            current: 0,
        }
    }

    componentDidMount() {
        this.fetchTargets();
    }

    fetchTargets = async () => {
        this.setState({
            fetching: true // requesting..
        });

        const info = await Promise.all([
            service.getTargets(),
        ]);

        const fileList = []
        const myRe = /targets\/.*/g;
        for (let i=0; i<info[0].data.images.length; i++) {
            const imgUrl = info[0].data.images[i]
            var name = imgUrl.match(myRe);
            fileList.push({
                uid: i,
                name: name,
                status: 'done',
                url: imgUrl,
                thumUrl: imgUrl
            });
        }
        info[0].data.images.forEach(element => console.log(element));
        this.setState({
            fileList,
            fetching: false // done!
        });
    }

    next() {
        const current = this.state.current + 1;
        this.setState({ current });
    }
    
    prev() {
        const current = this.state.current - 1;
        this.setState({ current });
    }

    render() {
        const { current, fileList } = this.state;

        const targetProps = {
            name: 'file',
            action: 'https://www.mocky.io/v2/5cc8019d300000980a055e76',
            listType: 'picture',
            accept: 'image/*',
            fileList: fileList,
            onChange(info) {
                if (info.file.status !== 'uploading') {
                console.log(info.file, info.fileList);
                }
                if (info.file.status === 'done') {
                message.success(`${info.file.name} file uploaded successfully`);
                } else if (info.file.status === 'error') {
                message.error(`${info.file.name} file upload failed.`);
                }
            },
            beforeUpload(file) {
                const isLt10M = file.size / 1024 / 1024 < 10;
                if (!isLt10M) {
                message.error('Image must be maller than 10MB!');
                }
                return isLt10M;
            },
        };
        
        const videoProps = {
            name: 'file',
            multiple: false,
            action: 'https://www.mocky.io/v2/5cc8019d300000980a055e76',
            accept: 'video/*',
            onChange(info) {
                const { status } = info.file;
                if (status !== 'uploading') {
                console.log(info.file, info.fileList);
                }
                if (status === 'done') {
                message.success(`${info.file.name} file uploaded successfully.`);
                } else if (status === 'error') {
                message.error(`${info.file.name} file upload failed.`);
                }
            },
            beforeUpload(file) {
                // const isVideo = file.type === 'video/*';
                // if (!isVideo) {
                // message.error('You can only upload Video File!');
                // }
                const isLt10M = file.size / 1024 / 1024 < 10;
                if (!isLt10M) {
                message.error('Video must be smaller than 10MB!');
                }
                return isLt10M;
            },
        };

        const { Step } = Steps;
        const steps = [
            {
                title: 'Step 1',
                description: 'Set Your Target Image',
                content: 
                    <div>
                        <Upload {...targetProps}>
                            <Button>
                                <Icon type="upload" /> Click to Upload
                            </Button>
                        </Upload>
                    </div>,
            },
            {
                title: 'Step 2',
                description: 'Upload Your Video',
                content:
                    <div>
                        <Dragger {...videoProps}>
                            <p className="ant-upload-drag-icon"><Icon type="inbox" /></p>
                            <p className="ant-upload-text">Click or drag Video to this area to upload</p>
                            <p className="ant-upload-hint">
                            Video must be smaller than 10MB
                            </p>
                        </Dragger>
                    </div>,
            },
            {
                title: 'Step 3',
                description: 'Choose Your Replacement Type',
                content: 
                    <div className="radioWrapper">
                        <Radio.Group defaultValue="blur" buttonStyle="solid" size="large">
                            <Radio.Button value="blur"> Blur </Radio.Button>
                            <Radio.Button value="emoji"> Emoji 😎</Radio.Button>
                            <Radio.Button value="image"> Transparent Image </Radio.Button>
                    </Radio.Group>  
                    </div>,
            },
        ];

        return (
        <div className="homePageWrapper page2" id="page2">
            <div className="parallaxBg top">
            <svg
                width="1440px"
                height="557px"
                viewBox="0 0 1440 557"
                stroke="none"
                strokeWidth="1"
                fill="none"
                fillRule="evenodd"
            >
                {svgChildren}
            </svg>
            </div>
            <div className="page">
            <h2> Try with Your Own Image & Video! </h2>
            <div>
                <Steps current={current}>
                {steps.map(item => (
                    <Step key={item.title} title={item.title} />
                ))}
                </Steps>
                <div className="steps-content">{steps[current].content}</div>
                <div className="steps-action">
                {current > 0 && (
                    <Button style={{ marginRight: 8 }} onClick={() => this.prev()}>
                    Previous
                    </Button>
                )}
                {current < steps.length - 1 && (
                    <Button type="primary" onClick={() => this.next()}>
                    Next
                    </Button>
                )}
                {current === steps.length - 1 && (
                    <Button type="primary" onClick={() => message.success('Processing complete!')}>
                    Done
                    </Button>
                )}
                </div>
            </div>
        </div>
    </div>
    );
  }
}

export default Page2;