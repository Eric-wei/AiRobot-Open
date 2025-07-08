/**
 * @Author: zhujinlong
 * @Date:   2025-04-21 16:46:29
 * @Last Modified by:   zhujinlong
 * @Last Modified time: 2025-04-22 11:29:49
 */

class BaiduRtcAgentClient {
  constructor() {
    this.AppID = '';
    this.AgentID = '';
    this.gAgentStarted = false;
    this.AgentApiHost = 'https://ai.agent.kaywang.cn/api';
  }

  Start(param) {
    this.AppID = param.appid;
    console.log('Agent.Start appid: ' + this.AppID);

    if (param.apihost) {
      this.AgentApiHost = param.apihost;
    }

    const xmlHttp = new XMLHttpRequest();
    xmlHttp.open('POST', this.AgentApiHost + '/v1/aiagent/generateAIAgentCall', true);
    xmlHttp.setRequestHeader('Content-Type', 'application/json');

    const data = {
      app_id: this.AppID,
      quick_start: true,
      config: JSON.stringify(param.cfg)
    };

    const that_agent = this;

    xmlHttp.onreadystatechange = function () {
      if (xmlHttp.readyState === 4) {
        if (xmlHttp.status === 200) {
          console.log(xmlHttp.responseText);
          let response = JSON.parse(xmlHttp.responseText);
          if (response.ai_agent_instance_id) {
            that_agent.gAgentStarted = true;
            that_agent.AgentID = response.ai_agent_instance_id;
            let userID = that_agent.AgentID;
            let Token = response.context.token;

            if (response.context && response.context.uid) {
              userID = response.context.uid;
            }

            if (response.context && response.context.appid) {
              that_agent.AppID = response.context.appid;
              param.appid = that_agent.AppID;
            }

            that_agent.loginBRTC(Object.assign(param, {
              roomname: that_agent.AgentID,
              userid: userID,
              token: Token
            }));
          }
        }
      }
    };

    xmlHttp.send(JSON.stringify(data));
  }

  Stop() {
    return new Promise((resolve, reject) => {
      if (!this.gAgentStarted) {
        resolve();
        return;
      }
      this.gAgentStarted = false;
      console.log('Agent.Stop begin.');

      const xmlHttp = new XMLHttpRequest();
      xmlHttp.open('POST', this.AgentApiHost + '/v1/aiagent/stopAIAgentInstance', true);
      xmlHttp.setRequestHeader('Content-Type', 'application/json');
      const data = {
        app_id: this.AppID,
        ai_agent_instance_id: this.AgentID
      };

      xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState === 4) {
          if (xmlHttp.status === 200) {
            console.log('Agent.Stop OK:' + xmlHttp.responseText);
            resolve();
          } else {
            console.log('Agent.Stop failed:' + xmlHttp.responseText);
            reject();
          }
        }
      };
      xmlHttp.send(JSON.stringify(data));
      window.BRTC_Stop();
    });
  }

  GetAgentID() {
    return this.AgentID;
  }

  loginBRTC(p) {
    window.BRTC_Start(
      Object.assign(p, {
        aspublisher: true,
        usingdatachannel: true,
        usingvideo: false,
        usingaudio: true,
        showvideobps: false,
        autosubscribe: true,
        autoplaymuted: false,
        autopublish: true,
        showspinner: false,
        shownovideo: false,
        userevent: true,
        sessionevent: true,
        linkdownevent: function () {
          console.log('linkdownevent');
        },
        linkupevent: function () {
          console.log('linkupevent');
        },
        logintimeout: 10000,
        logintimeoutevent: function () {
          console.log('timeout');
        },
        mediastate: function (medium, on) {
          console.log('send medium ' + medium + ' is: ' + on);
        },
        remotevideoon: function (idx) {
          console.log('remotevideoon, index:' + idx);
        },
        remotevideooff: function (idx) {
          console.log('remotevideooff, index:' + idx);
        },
        remotevideocoming: function (id, display, attribute) {
          console.log('remotevideocoming, feedid:' + id + ':' + display + ':' + attribute);
        },
        remotevideoloading: function (idx) {
          console.log('remotevideoloading, index:' + idx);
        },
        remotevideoconnected_state: function (id, on) {
          console.log('remotevideoconnected_state, feedid:' + id + ' connected:' + on);
        },
        remotevideoleaving: function (id) {
          console.log('remotevideoleaving, feedid:' + id);
        },
        remotevideounpublished: function (id) {
          console.log('remotevideounpublished, feedid:' + id);
        },
        localvideoconnected_state: function (on) {
          console.log('localvideoconnected_state, connected:' + on);
        },
        localvideopublished_ok: function () {
          console.log('localvideopublished_ok.');
        },
        destroyed: function (error) {
          console.log('destroyed:', error);
        },
        onlocalstream: function (stream, name) {
          console.log('onlocalstream name: ' + name);
        },
        onlocalstream_end: function (name) {
          console.log('onlocalstream_end name: ' + name);
        },
        remotevideo_closed: function (feedid) {
          console.log('remotevideo_closed(feedid: ' + feedid + ') by server, please do SubScribing again');
        }
      })
    );
  }

  sendMessageToUser(msg, uid) {
    window.BRTC_SendMessageToUser(msg, uid);
  }

  Version() {
    return 'V1.0.4';
  }
}

export default BaiduRtcAgentClient; 