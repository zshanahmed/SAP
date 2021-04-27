function custom_fill_notification_list(data) {
    var menus = document.getElementsByClassName(notify_menu_class);
    if (menus) {
        var messages = data.unread_list.map(function (item) {
            var message = "";
            if(typeof item.verb !== 'undefined'){
                message = message + " " + item.verb;
            }
            return '<a class="dropdown-item" type="button">' + message + '</a> <hr/>';
        }).join('')

        for (var i = 0; i < menus.length; i++){
            menus[i].innerHTML = messages;
        }
    }
}