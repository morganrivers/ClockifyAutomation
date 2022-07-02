/*
 * jquery.sidemenu.js
 * https://github.com/kami30k/jquery.sidemenu.js
 *
 * Copyright 2015 kami.
 * Released under the MIT license.
 */
 var list = [];

;(function($) {
  /**
   * Initialize side menu.
   */
  function initialize() {
    $('[data-role=sidemenu-toggle]').on('click', function(e) {
      e.preventDefault();
      $('[data-role=sidemenu-container]').toggleClass('is-active');
        var element = document.getElementById("sidemenu_container");
        // alert(element)
        var col1 = document.getElementById("col1");
        var col2 = document.getElementById("col2");
        if(element.classList.contains("is-active")) {
          col1.style.width = "45%"
          col2.style.width = "45%"
        } else {
          col1.style.width = "50%"
          col2.style.width = "50%"
        }
    });
    // alert("Your book is overdue"); 
    $('.mybutton').on('click', function () {
        $('.example').toggleClass('is--hidden');
    })

    $("#shoppingItem").change(function() { 
        var item = $(this).val();   
        item_id = "shoppingItem_"+item
        if (document.getElementById(item_id)) {
          //already exists
          return
        }
        if (!/\S/.test(item)) {
          return
        }
            // string is not empty and not just whitespace
          $("<li class='tile' style='padding: 5px;' id='"+item_id+"'>"+item+"</li>").prependTo(".shopping_item_list");
          $(".tile").removeClass("middle");   
          $(".shopping_item_list li:nth-child(3n+2)").addClass("middle");
          document.getElementById('shoppingItem').value = "";
          $('#shoppingItem_'+item_id).on('click', function () {
              // $(this).remove();
              // alert($(this).item_id());

              alert($(this).closest('li').id);
              $(this).closest("li").remove();
          })

    });

    $("#dynamic-list").click(function(event) {
      if(event.target.id !== "dynamic-list")
        document.getElementById(event.target.id).remove();
      // list.push(i);
    });

    // // return json data from any file path (asynchronous)
    // function getJSON(path) {
    //     return fetch(path).then(response => response.json());
    // }

    // // load json data; then proceed
    // getJSON('config.json').then(info => {
    //     // get title property and log it to the console
    //     var title = info.title;
    //     console.log(title);  
    // }

  }

  $(document).ready(function() {
    initialize();

    // Support for Turbolinks
    if (typeof Turbolinks !== 'undefined') {
      $(document).on('page:load', function() {
        initialize();
      });
    }


  });
})(jQuery);