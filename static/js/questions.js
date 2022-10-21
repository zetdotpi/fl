// Grab all elements with the class "hasTooltip"
$('.hasTooltip').each(function() { // Notice the .each() loop, discussed below
    $(this).qtip({
        content: {
            text: $(this).next('div') // Use the "div" element next to this for the content
        }
    });
});	