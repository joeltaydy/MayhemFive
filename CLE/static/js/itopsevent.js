//jQuery time
var current_fs, next_fs, previous_fs; //fieldsets
var left, opacity, scale; //fieldset properties which we will animate
var animating; //flag to prevent quick multi-click glitches

$(".next").click(function(){
	if(animating) return false;
	animating = true;
	
	current_fs = $(this).parent();
	next_fs = $(this).parent().next();
	
	//activate next step on progressbar using the index of next_fs
	$("#progressbar li").eq($("fieldset").index(next_fs)).addClass("active");
	//show the next fieldset
	next_fs.show(); 
	//hide the current fieldset with style
	current_fs.animate({opacity: 0}, {
		step: function(now, mx) {
			//as the opacity of current_fs reduces to 0 - stored in "now"
			//1. scale current_fs down to 80%
			scale = 1 - (1 - now) * 0.2;
			//2. bring next_fs from the right(50%)
			left = (now * 50)+"%";
			//3. increase opacity of next_fs to 1 as it moves in
			opacity = 1 - now;
			current_fs.css({
        'transform': 'scale('+scale+')',
        'position': 'absolute'
      });
			next_fs.css({'left': left, 'opacity': opacity});
		}, 
		duration: 800, 
		complete: function(){
			current_fs.hide();
			animating = false;
		}, 
		//this comes from the custom easing plugin
		easing: 'easeInOutBack'
	});
});

$(".previous").click(function(){
	if(animating) return false;
	animating = true;
	
	current_fs = $(this).parent();
	previous_fs = $(this).parent().prev();
	
	//de-activate current step on progressbar
	$("#progressbar li").eq($("fieldset").index(current_fs)).removeClass("active");
	
	//show the previous fieldset
	previous_fs.show(); 
	//hide the current fieldset with style
	current_fs.animate({opacity: 0}, {
		step: function(now, mx) {
			//as the opacity of current_fs reduces to 0 - stored in "now"
			//1. scale previous_fs from 80% to 100%
			scale = 0.8 + (1 - now) * 0.2;
			//2. take current_fs to the right(50%) - from 0%
			left = ((1-now) * 50)+"%";
			//3. increase opacity of previous_fs to 1 as it moves in
			opacity = 1 - now;
			current_fs.css({'left': left});
			previous_fs.css({'transform': 'scale('+scale+')', 'opacity': opacity});
		}, 
		duration: 800, 
		complete: function(){
			current_fs.hide();
			animating = false;
		}, 
		//this comes from the custom easing plugin
		easing: 'easeInOutBack'
	});
});

$(".submit").click(function(){
	return false;
})

//Number Picker Plugin - TobyJ
(function ($) {
    $.fn.numberPicker = function() {
      var dis = 'disabled';
      return this.each(function() {
        var picker = $(this),
            p = picker.find('button:last-child'),
            m = picker.find('button:first-child'),
            input = picker.find('input'),                 
            min = parseInt(input.attr('min'), 10),
            max = parseInt(input.attr('max'), 10),
            inputFunc = function(picker) {
              var i = parseInt(input.val(), 10);
              if ( (i <= min) || (!i) ) {
                input.val(min);
                p.prop(dis, false);
                m.prop(dis, true);
              } else if (i >= max) {
                input.val(max);
                p.prop(dis, true); 
                m.prop(dis, false);
              } else {
                p.prop(dis, false);
                m.prop(dis, false);
              }
            },
            changeFunc = function(picker, qty) {
              var q = parseInt(qty, 10),
                  i = parseInt(input.val(), 10);
              if ((i < max && (q > 0)) || (i > min && !(q > 0))) {
                input.val(i + q);
                inputFunc(picker);
              }
            };
        m.on('click', function(){changeFunc(picker,-1);});
        p.on('click', function(){changeFunc(picker,1);});
        input.on('change', function(){inputFunc(picker);});
        inputFunc(picker); //init
      });
    };
  }(jQuery));
  
  
  $(document).on('ready', function(){
    
    $('.plusminus').numberPicker();
    
    //add dynamically:
    $('<div class="plusminus horiz"><button></button><input type="number" name="qty" value="1" min="1" max="5"><button></button></div>').numberPicker().appendTo('body');
    
  });