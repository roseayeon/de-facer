import React from 'react';
import { Upload, Button, Icon, message, Steps, Result, Spin, Card, Col, Row, Checkbox, Tabs, Input } from 'antd';
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
const { Step } = Steps;
const { Meta } = Card; 
const { TabPane } = Tabs;

class Page2 extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            fileList: [],
            targetImgs: [],
            current: 0,
            radioValue: 'blur',
            videoFile: undefined,
            replaceImg: [],
            showLoading: false,
            responseUrl: '',
            videoMode: 'uploadVideo',
            videoUrl: '',
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
            var name = ''+imgUrl.match(myRe)+'';
            name = name.substring(8);
            fileList.push({
                uid: i,
                name: name,
                status: 'done',
                url: imgUrl,
                thumbUrl: imgUrl
            });
        }
        this.setState({
            fileList,
            fetching: false // done!
        });
    }

    postVideo  = async () => {
        this.setState({
            fetching: true, // requesting..
            showLoading: true,
        });
        const info = await Promise.all([
            service.postProcess(this.state.targetImgs, this.state.videoFile, this.state.replaceImg)
        ]).then( 
            response => { 
                console.log(response); 
                this.setState({
                    responseUrl: response[0].data.url
                })
            })
        this.setState({
            fetching: false, // done!
            showLoading: false,
        });
        message.success('De-facing complete!')
    }

    clickPrev = () => {
        if (this.state.replaceImg.length === 0) {
            this.setState({
                radioValue: 'blur'
            })
        }
        this.prev()
    }

    next() {
        const current = this.state.current + 1;
        this.setState({ current });
    }
    
    prev() {
        const current = this.state.current - 1;
        this.setState({ current });
    }

    onVideoChange = (file) => {
        this.setState({ videoFile: file});
    }

    onRadioChange = (key) => {
        this.setState({radioValue: key})
    }

    onVideoModeChange = (key) => {
        this.setState({videoMode: key})
    }

    clickedImage = (e) => {
        var file = e.target.value;
        var index = this.state.targetImgs.indexOf(file);
        if (index > -1){
            let newImgLst = this.state.targetImgs
            newImgLst.splice(index, 1)
            this.setState({
                targetImgs: newImgLst
            })
        } else {
            this.setState({
                targetImgs: [
                    ...this.state.targetImgs,
                    file
                ]
            })
        }
    }

    onReplaceImageChange = (file) => {
        this.setState({
            replaceImg: [file.file],
        })
    }

    onRealtimeClick = async () => {
        this.setState({
            fetching: true // requesting..
        });

        const info = await Promise.all([
            service.postRealTime(this.state.targetImgs, this.state.videoUrl, this.state.replaceImg),
        ]).then( 
            response => { 
               if(response[0].status === 200){
                    window.open("http://"+window.location.hostname+"/real_time", "_blank")
               }
        })

        this.setState({
            fetching: false // done!
        });
    }

    getCardStyle = (url) => {
        let retVal = {}
        var index = this.state.targetImgs.indexOf(url);
        if ( index > -1 ){
            var position = this.state.fileList.findIndex((e)=> e.url === url)
            if((position+1)%4 === 0){
                retVal = { width: 210, border: "2px solid #1890ff", marginBottom: -1 }
            } else {
                retVal = { width: 210, border: "2px solid #1890ff", marginBottom: -2 }
            }
        } else {
            retVal = { width: 210 }
        }
        return retVal
    }

    render() {
        const { current, fileList, responseUrl } = this.state;

        const targetProps = {
            name: 'file',
            action(file) {
                return Promise.all([
                    service.postTarget(file),
                ])
                .then(
                    message.success(`${file.name} file uploaded successfully`)
                )
            },
            listType: 'picture',
            accept: 'image/*',
            fileList: fileList,
            showUploadList: false,
            onChange: this.fetchTargets,
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
            action: this.onVideoChange,
            accept: 'video/*',
            showUploadList: false,
            beforeUpload(file) {
                const isLt10M = file.size / 1024 / 1024 < 10;
                if (!isLt10M) {
                message.error('Video must be smaller than 10MB!');
                }
                return isLt10M;
            },
        };

        const replaceProps = {
            name: 'file',
            action: 'https://www.mocky.io/v2/5cc8019d300000980a055e76',
            listType: 'picture',
            accept: 'image/png',
            fileList: this.state.replaceImg,
            showUploadList: {
                showRemoveIcon: false,
                showPreviewIcon: true,
                showDownloadIcon: false,
            },
            onChange: this.onReplaceImageChange,
            beforeUpload(file) {
                const isPNG = file.type.match('image/png');
                if(!isPNG) {
                    message.error('Image should be PNG.');
                }
                const isLt10M = file.size / 1024 / 1024 < 10;
                if (!isLt10M) {
                    message.error('Image must be maller than 10MB!');
                }
                return isLt10M && isPNG;
            },
        }

        
        const steps = [
            {
                title: 'Target Image',
                description: "Choose a image that you don't want to replace",
                content: 
                    <div>
                        <Upload {...targetProps}>
                            <Button className="uploadButton">
                                <Icon type="upload" /> Click to Upload
                            </Button>
                            We recommend using an image which is similar to the target face in the video.
                        </Upload>
                        <Row gutter={16}>
                            <Checkbox.Group value={this.state.targetImgs}>
                            {
                                fileList.map(item => (
                                    <Col span={6} key={item.name}>
                                        <Card
                                            hoverable
                                            style={this.getCardStyle(item.url)}
                                            cover={<img alt={item.name} src={item.thumbUrl} />}
                                        >
                                            <Meta title={<Checkbox value={item.url} onChange={this.clickedImage}>{ item.name } </Checkbox>} />
                                        </Card>
                                    </Col>
                                ))
                            }
                            </Checkbox.Group>
                        </Row>
                    </div>,
            },
            {
                title: 'Replacement Type',
                description: 'choose either blur or transparent image',
                content: 
                    <div>
                        <Tabs defaultActiveKey={this.state.radioValue} activeKey={this.state.radioValue} size="large" onChange={this.onRadioChange}>
                            <TabPane
                            tab={
                                <span>
                                Blur
                                </span>
                            }
                            key="blur"
                            >
                            <div>
                                <Result
                                    icon={<Icon type="smile" />}
                                    title="If you want to blur others' faces, keep going!"
                                />
                            </div>
                            </TabPane>
                            <TabPane
                            tab={
                                <span>
                                Image
                                </span>
                            }
                            key="image"
                            >
                            <div>
                                <div className="resultWrapper">
                                    <Result
                                        icon={<Icon type="file-image" />}
                                        title="Upload a transparent image (.png) that you want to replace others' faces!"
                                    />
                                </div>
                                <div className="uploadWrapper">
                                    <Upload {...replaceProps}>
                                        <Button>
                                            <Icon type="upload" /> Click to Upload
                                        </Button>
                                    </Upload>
                                </div>
                            </div>
                            </TabPane>
                        </Tabs>
                    </div>
                    ,
            },
            {
                title: 'Video',
                description: 'choose either video or real-time',
                content:
                    <div className="resultWrapper">
                        <Tabs defaultActiveKey={this.state.videoMode} activeKey={this.state.videoMode} size="large" onChange={this.onVideoModeChange}>
                            <TabPane
                            tab={
                                <span> <Icon type="upload" /> Upload a video </span>
                            }
                            key="uploadVideo"
                            >
                            {
                                this.state.videoFile === undefined &&
                                <Dragger {...videoProps}>
                                    <p className="ant-upload-drag-icon"><Icon type="inbox" /></p>
                                    <p className="ant-upload-text">Click or drag Video to this area to upload</p>
                                    <p className="ant-upload-hint">
                                    Video must be smaller than 10MB
                                    </p>
                                </Dragger>
                            }
                            {
                                this.state.videoFile !== undefined && responseUrl === '' &&
                                <Result
                                    status="success"
                                    title="Video is Uploaded"
                                    subTitle="Click Done button to deface your video"
                                    extra={[
                                    <Button key="buy" onClick={()=> this.setState({videoFile: undefined})}>Upload other video</Button>,
                                    ]}
                                />
                            }
                            {
                                responseUrl !== '' &&
                                <Result
                                    icon={<Icon type="download" />}
                                    title="Get the De-faced Video"
                                    extra={[
                                        <Button key="buy" onClick={()=> window.open(responseUrl, "_blank")}>Download</Button>,
                                    ]}
                                />
                            }
                            </TabPane>
                            <TabPane
                                tab={
                                    <span> <Icon type="video-camera" /> Play with real-time </span>
                                }
                                key="realtime"
                            >
                            <Result
                                icon={<Icon type="video-camera" />}
                                title="Great! Let's deface with webcam in real-time!"
                                subTitle={<div>URL:<Input placeholder="Input Video URL (ex. rtsp://*)" style={{width: 350, marginLeft: 20}} value={this.state.videoUrl} onChange={e => this.setState({videoUrl: e.target.value})}/></div>}
                                extra={<Button type="primary" onClick={this.onRealtimeClick}>Play with real-time</Button>}
                            />
                            </TabPane>
                        </Tabs>
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
                { svgChildren }
            </svg>
            </div>
            <div className="page">
            <h2> Try with Your Own Image & Video! </h2>
            <Spin spinning={this.state.showLoading} tip="De-facing...">
                <div>
                    <Steps current={current}>
                        {
                            steps.map(item => (
                                <Step key={item.title} title={item.title} description={item.description} />
                            ))
                        }
                    </Steps>
                    <div className="steps-content">{steps[current].content}</div>
                        {
                            current === 1 && (
                                <div className="instruction">
                                    <p>You chose <b>{this.state.radioValue}</b>  for the replacement type.</p>
                                </div>
                            ) 
                        }
                    <div className="steps-action">
                    {
                        current > 0 &&  responseUrl === '' && (
                        <Button style={{ marginRight: 8 }} onClick={this.clickPrev}>
                        Previous
                        </Button>
                    )}
                    {
                        current < steps.length - 1 && responseUrl === '' && (
                        <Button type="primary" onClick={() => this.next()} disabled={this.state.targetImgs.length === 0}>
                        Next
                        </Button>
                    )}
                    {
                        current === steps.length - 1 && responseUrl === '' &&(
                        <Button type="primary" onClick={this.postVideo} disabled={this.state.videoFile === undefined}>
                            Done
                        </Button>
                    )}
                    </div>
                </div>
            </Spin>
        </div>
    </div>
    );
  }
}

export default Page2;
