/* ----------------------------- 
Pre Loader
----------------------------- */
$(window).load(function() {
    'use strict';
    $('.loader').delay(200).fadeOut();
    $('.preloader').delay(400).fadeOut('slow');
});
/* ----------------------------- 
Cloud movement
-----------------------------  */
$(document).ready(function() {
    'use strict';
    $('.cloud').plaxify()
    $.plax.enable()
});
/* ----------------------------- 
Element slide animations
-----------------------------  */
$(window).load(function() {
    'use strict';
    $('html').find('.animated').each(function() {
        var element = $(this),
            animation = element.data('animation'),
            animationDelay = element.data('animation-delay');
        if (animationDelay) {
            setTimeout(function() {
                element.addClass(animation + " visible");
            }, animationDelay);
            setTimeout(function() {
                element.removeClass(animation);
            }, 5000);
        } else {
            element.addClass(animation + " visible");
        }
    });
});
/* ----------------------------- 
Search Input expand
-----------------------------  */
(function() {
    var morphSearch = document.getElementById('morphsearch'),
        input = morphSearch.querySelector('input.morphsearch-input'),
        ctrlClose = morphSearch.querySelector('span.morphsearch-close'),
        isOpen = isAnimating = false,
        // show/hide search area
        toggleSearch = function(evt) {
            // return if open and the input gets focused
            if (evt.type.toLowerCase() === 'focus' && isOpen) return false;
            var offsets = morphsearch.getBoundingClientRect();
            if (isOpen) {
                classie.remove(morphSearch, 'open');
                // trick to hide input text once the search overlay closes 
                // todo: hardcoded times, should be done after transition ends
                if (input.value !== '') {
                    setTimeout(function() {
                        classie.add(morphSearch, 'hideInput');
                        setTimeout(function() {
                            classie.remove(morphSearch, 'hideInput');
                            input.value = '';
                        }, 300);
                    }, 500);
                }
                input.blur();
            } else {
                classie.add(morphSearch, 'open');
            }
            isOpen = !isOpen;
        };
    // events
    input.addEventListener('focus', toggleSearch);
    ctrlClose.addEventListener('click', toggleSearch);
    // esc key closes search overlay
    // keyboard navigation events
    document.addEventListener('keydown', function(ev) {
        var keyCode = ev.keyCode || ev.which;
        if (keyCode === 27 && isOpen) {
            toggleSearch(ev);
        }
    });
})();
