function syntaxHighlight(json) {
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        var cls = 'number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'key';
            } else {
                cls = 'string';
            }
        } else if (/true|false/.test(match)) {
            cls = 'boolean';
        } else if (/null/.test(match)) {
            cls = 'null';
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}

function merge_copy(list1, list2) {
    // Merge two arrays without altering first
    return $.merge($.merge([], list1), list2);
}

function lists_intersection(list1, list2) {
    return $.map(list1, function(el){
        return $.inArray(el, list2) < 0 ? null : el;
    })
}

function in_array_or_equal(value, data) {
    return Boolean(((value == data) || ($.inArray(value, data) >= 0)))
}