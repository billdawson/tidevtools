/*global Ti, Titanium, alert, JSON */
Titanium.UI.setBackgroundColor('#000');
Titanium.UI.createWindow({  
    title:'Test',
    backgroundColor:'#fff',
	fullscreen: true,
	exitOnClose: true,
	url: 'win.js'
}).open();
