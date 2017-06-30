/**
 * Created by artem on 21.11.16.
 */

app.factory('WebsocketData', function ($websocket) {
    // Open a WebSocket connection

    var protocol = 'ws://';

    if (window.location.protocol === 'https:') {
        protocol = 'wss://';
    }

    var dataStream = $websocket(protocol + window.location.host + "/notifications/");

    var notifications = [];

    var show_toast = [];

    dataStream.onMessage(function (message) {
        show_toast.splice(0, show_toast.length);
        notifications.splice(0, notifications.length);
        var data = JSON.parse(message.data)

        if (data.action == 'user_picture'){
            if (data.url.length>0)
                angular.element('#userprofile_picture')[0].src = data.url;
            return
        }

        if (data.action == 'update_notifications'){
            setTimeout(function() {
                dataStream.send(JSON.stringify({ action: 'get_notification' }));
            }, 1000);
            return
        }

        for (i in data){
            notifications.push(data[i])
        }
        if (notifications.length>0){
            var audio = new Audio('/static/ui/ring.mp3');
            audio.play();
            show_toast.push(1);
        }
    });
    dataStream.onClose(function () {
        dataStream.reconnect();
    })
    dataStream.onError(function () {
        dataStream.reconnect();
    })
    var methods = {
        notifications: notifications,
        show_toast: show_toast,
        mark_all_as_read: function() {
          dataStream.send(JSON.stringify({ action: 'mark_all_as_read' }));
        }
    };

    return methods;
})
    .controller('NotificationController', function ($scope, WebsocketData, toastr) {
    $scope.WebsocketData = WebsocketData;
    var notifications = $scope.WebsocketData.notifications;
    $scope.$watchCollection('WebsocketData.show_toast', function(newVal, oldVal) {
        if(newVal.length>0) {
            for (i in notifications) {
                toastr.info(notifications[i].message, notifications[i].title);
            }
        }
    });
});