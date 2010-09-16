var notification = Ti.UI.createNotification({
	duration: Ti.UI.NOTIFICATION_DURATION_LONG
	
});
function showStatus(text)
{
	notification.hide();
	notification.message = text;
	notification.show();
}
