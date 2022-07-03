/*
 * jquery.sidemenu.js
 * https://github.com/kami30k/jquery.sidemenu.js
 *
 * Copyright 2015 kami.
 * Released under the MIT license.
 */
;(function($) {
  function load_categories(categories) {
    var html_insertion = "<table class='table_categorize'>"
            +
                    "<tr>" 
                      +"<th width = '33%'>Project</th>"
                      +"<th width = '67%'>Tags (Click to remove)</th>"
                    +"</tr>"
    // <tr>
    //  <td>
    //     <div class="green box" id="myDIV">You have selected <strong>red checkbox</strong> so i am here</div>
    //   </td>
    //   <td>
    //     <div class="green box">You have selected <strong>green checkbox</strong> so i am here</div>
    //   </td>
    // </tr> 
    // <tr>
    //  <td>
    //     <div class="red box" id="myDIV"><div>Irrelevant</div><input placeholder="add search string" type="text" id="shoppingItem" /></div>
    //   </td>
    //   <td>
    //     <div class="red box" id="myDIV">
    //       <ul class="shopping_item_list" id = "dynamic-list">
    //       </ul>
    //     </div>
    //   </td>
    // </tr> 
    // <tr>
    //  <td>
    //     <div class="blue box" id="myDIV">You have selected <strong>red checkbox</strong> so i am here</div>
    //   </td>
    //   <td>
    //     <div class="blue box">You have selected <strong>green checkbox</strong> so i am here</div>
    //   </td>
    // </tr>

    // alert(JSON.stringify(categories))
    var key;
    // first, create the categories
    for (key in categories) {
      html_insertion = html_insertion
        +"<tr><td><div class='green box' id='title_"+key+"'>"
        + key
       +"<br /><input placeholder='add search string' type='text' id='input_field_"
       +key+"' />"
       +"</div></td>"
       +"<td><div class='green box' id='content_"+key+"'></div></td></tr>"
    }
    html_insertion = html_insertion + "</table>"
    $(html_insertion).appendTo("#col2")
    // for (key in categories) {
    //   var rules = categories[key].rules
    //   var index
    //   for (index in rules){ 
    //     rule = rules[index]
    //     $("<li class='tile' style='padding: 5px;' id='"+key+'_'+index+"'>"+rule+"</li>").prependTo(".shopping_item_list");
    //   }
    // }

    // document.getElementById("dynamic-list").remove();
  }

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
          collapsible_topnav.style.width="90%"
        } else {
          col1.style.width = "50%"
          col2.style.width = "50%"
          collapsible_topnav.style.width="100%"
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
          // $('#shoppingItem_'+item_id).on('click', function () {
          //     // $(this).remove();
          //     // alert($(this).item_id());

          //     alert($(this).closest('li').id);
          //     $(this).closest("li").remove();
          // })

    });



    $("#dynamic-list").click(function(event) {
      if(event.target.id !== "dynamic-list")
        document.getElementById(event.target.id).remove();
      // list.push(i);
    });

    $("#load_json").click(function(event) {

      $.ajax({ 
          url: "/api/load_json_categories/" 
      }).done(function(categories) { 
          load_categories(categories) 
      }); 

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
    // $('#date1').datepicker({
    //     changeMonth: true,
    //     changeYear: true,
    //     showButtonPanel: true,
    //     dateFormat: "m/d/yy"
    // });



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