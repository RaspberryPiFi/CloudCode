goog.provide('pisync.ui.control');

goog.require('goog.dom');
goog.require('goog.net.XhrIo');
goog.require('goog.style');
goog.require('goog.ui.Slider');

var NOTIFY_INFO = 0;
var NOTIFY_ERROR = 1;

/**
 * Nothing to do here
 * @constructor
*/
pisync.ui.control = function() {};

/**
 * Sets up volume slider and event listener
 */
pisync.ui.control.prototype.setUpTestToneEvents = function(){
  var dom_array = goog.dom.getElementsByClass('test_tone');
  for (var i = 0; i < dom_array.length; ++i) {
    var device_key = dom_array[i].getAttribute('data-device-key');
    goog.events.listen(dom_array[i],
                       goog.events.EventType.CLICK,
                       goog.bind(this.handleAction,this,'test_tone',device_key));
  }
};

/**
 * Sets up volume slider and event listener
 */
pisync.ui.control.prototype.setUpVolumeSlider = function(device_key) {
  var el = document.getElementById('volume_slider');
  this.s = new goog.ui.Slider();
  this.s.decorate(el);
  goog.events.listen(this.s.getContentElement(),
                     [goog.events.EventType.KEYUP,
                      goog.events.EventType.MOUSEUP],
                      goog.bind(this.handleAction,this,'set_volume',device_key));
};

/**
 * Sets up control event listeners
 */
pisync.ui.control.prototype.setUpControlEvents = function(device_key) {
  //TODO: Disable pause button when party mode
  this.setUpVolumeSlider(device_key);
  this.party_mode = (device_key === 'party_mode');
  var skip_backward = goog.dom.getElement('skip_backward_button');
  var skip_forward = goog.dom.getElement('skip_forward_button');
  var stop = goog.dom.getElement('stop_button');
  var pause = goog.dom.getElement('pause_button');
  
  goog.events.listen(skip_backward, goog.events.EventType.CLICK,
                     goog.bind(this.handleAction,this,'skip_backward', device_key));
  goog.events.listen(skip_forward, goog.events.EventType.CLICK,
                     goog.bind(this.handleAction,this,'skip_forward', device_key));
  if (device_key === 'party_mode') {
    goog.events.listen(stop, goog.events.EventType.CLICK,
                     goog.bind(this.handleAction,this,'stop', device_key));
  } else {
    goog.events.listen(pause, goog.events.EventType.CLICK,
                     goog.bind(this.handlePlayPauseClick,this, device_key));
  }
  this.startPolling(device_key);
};


/**
 * Starts polling
 */
pisync.ui.control.prototype.startPolling = function(device_key) {
  this.poll_xhr = new goog.net.XhrIo();
  goog.events.listen(this.poll_xhr, goog.net.EventType.SUCCESS, 
                    goog.partial(this.handleUpdate, this, device_key));
  goog.events.listen(this.poll_xhr, goog.net.EventType.ERROR, 
                    goog.partial(this.showNotification,NOTIFY_ERROR,'Error Getting Current Status!'));

  setTimeout(goog.bind(this.pollForUpdate,this,device_key),2000);
  
};

/**
 * Polls for an update
 */
pisync.ui.control.prototype.pollForUpdate = function(device_key) {
  var json_string = goog.json.serialize({'device_urlsafe_key': device_key});
  var url = '/device/get_update';
  this.poll_xhr.send(url, 'POST', json_string);
};

/**
 * Handles update from the cloud
 */
pisync.ui.control.prototype.handleUpdate = function(parent_obj, device_key) {
  var response = this.getResponse();
  if (response !== parent_obj.last_response) {
    var status = goog.json.parse(response);
    if (status.alive === true) {
      parent_obj.s.animatedSetValue(status.volume * 100);
      var play_pause_button = goog.dom.getElement('pause_button');
      if (status.state === 'playing') {
        goog.dom.getElement('now_playing_txt').innerHTML = status.now_playing;
        if (!parent_obj.party_mode){
          play_pause_button.src = '/static/images/pause.png';
          play_pause_button.setAttribute('data-button-state', 'pause');
        }
      } else if (status.state === 'paused') {
        goog.dom.getElement('now_playing_txt').innerHTML = status.now_playing;
        if (!parent_obj.party_mode){
          play_pause_button.src = '/static/images/play.png';
          play_pause_button.setAttribute('data-button-state', 'play');
        }
      } else {
        goog.dom.getElement('now_playing_txt').innerHTML = '';
      }
    } else {
      goog.dom.getElement('now_playing_txt').innerHTML = '';
    }
  }
  parent_obj.last_response = response;
  setTimeout(goog.bind(parent_obj.pollForUpdate,parent_obj,device_key),2000);
};

/**
 * Sets up event listeners for each song
 */
pisync.ui.control.prototype.setUpSongEvents = function(device_key,artist,album) {
  this.artist = artist;
  this.album = album;
  var dom_array = goog.dom.getElementsByClass('song_row');
  for (var i = 0; i < dom_array.length; ++i) {
    goog.events.listen(dom_array[i],
                       goog.events.EventType.CLICK,
                       goog.bind(this.handleSongClick,this,i, device_key));
  }
};

/**
 * Handles a push of the play/pause button
 */
 pisync.ui.control.prototype.handlePlayPauseClick = function(device_key){
  var play_pause_button =  goog.dom.getElement('pause_button');
  if (play_pause_button.getAttribute('data-button-state') == 'play') {
    play_pause_button.src = '/static/images/pause.png';
    play_pause_button.setAttribute('data-button-state', 'pause');
  } else {
    play_pause_button.src = '/static/images/play.png';
    play_pause_button.setAttribute('data-button-state', 'play');
  }
  this.handleAction('play_pause',device_key);
 };

/**
 * Handles song click 
 */
pisync.ui.control.prototype.handleSongClick = function(index, device_key) {
  var xhr = new goog.net.XhrIo();
  //TODO: Handle errors!
  goog.events.listen(xhr, goog.net.EventType.SUCCESS, 
                    goog.partial(this.showNotification,NOTIFY_INFO,'Action sent!'));
  goog.events.listen(xhr, goog.net.EventType.ERROR, 
                    goog.partial(this.showNotification,NOTIFY_ERROR,'Error Sending Action!'));
  var action = {};
  action.device_urlsafe_key = device_key;
  
  action.song_id = index;
  if (this.album !== false) {
    action.album = this.album;
  }
  if (this.artist !== false) {
    action.artist = this.artist;
  }
  var json_string = goog.json.serialize(action);
  var url = '/device/play';
  xhr.send(url, 'POST', json_string);
};

/**
 * Handles action click 
 */
pisync.ui.control.prototype.handleAction = function(action_type, device_key) {
  var xhr = new goog.net.XhrIo();
  goog.events.listen(xhr, goog.net.EventType.SUCCESS, 
                    goog.partial(this.showNotification,NOTIFY_INFO,'Action sent!'));
  goog.events.listen(xhr, goog.net.EventType.ERROR, 
                    goog.partial(this.showNotification,NOTIFY_ERROR,'Error Sending Action!'));
  var action = {};
  action.device_urlsafe_key = device_key;
  action.action = action_type;
  if (action_type === 'set_volume'){
    var arg = this.s.getValue() / 100;
    action.arg = arg;
  }
  var json_string = goog.json.serialize(action);
  var url = '/device/action';
  xhr.send(url, 'POST', json_string);
};

/**
 * Show notification bar
 */
pisync.ui.control.prototype.showNotification = function(event_type, message) {
  var notification_el = goog.dom.getElement('notification_bar');
  if (event_type === NOTIFY_INFO) {
    goog.dom.classes.swap(notification_el,'notification_error','notification_info');
  } else if (event_type === NOTIFY_ERROR) {
    goog.dom.classes.swap(notification_el,'notification_info','notification_error');
  }
  notification_el.innerHTML = message;
  goog.style.setStyle(notification_el, "display", "inline-block");
  setTimeout(function(){goog.style.setStyle(notification_el, "display", "none");},
            3000);
};

