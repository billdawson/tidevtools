/*global Ti, Titanium, alert, JSON */
var win = Ti.UI.currentWindow;
var mapview = Titanium.Map.createView({
    mapType: Titanium.Map.STANDARD_TYPE,
    region: {latitude:33.74511, longitude:-84.38993, 
            latitudeDelta:0.01, longitudeDelta:0.01}
});

win.add(mapview);

