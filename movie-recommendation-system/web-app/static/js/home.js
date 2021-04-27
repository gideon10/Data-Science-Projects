
var search_box = document.querySelector('.search-box');
var suggestions_box = document.getElementById('autocomplete-list');
var input_box = document.getElementById('search-txt');


$('#search-btn').on('click', function () {
    var movie_title = input_box.value;
    
    if (movie_title == '') {
        alert('Please, type a movie name!');
    }
    else {
        send_data_to_flask(movie_title);
        search_box.classList.remove('active');  // Hide autocomplete box.
    }
});


$(document).on('keypress', function(e) {
    if(e.which == 13) {
        var movie_title = e.target.value;

        if (movie_title == '') {
            alert('Please, type a movie name!');
        }
        else {
            send_data_to_flask(movie_title);
            search_box.classList.remove('active');  // Hide autocomplete box.
        }
    }
});


function send_data_to_flask(movie_title) {
    $('#loading').fadeIn();

    $.post('/recommend', {movie_title: movie_title}, function (response) {

        if (response == 'Sorry! The movie you requested is not in database. Please check the spelling or try with other movies!') {
            $('#fail').css('display', 'flex');
            $('#results').css('display','none');
            $('#loading').delay(500).fadeOut();
        }
        else {
            $('#fail').css('display', 'none');
            $('#results').css('display','block');
            $('#results').html(response);
            $('#loading').delay(500).fadeOut();
        }
    });
}


function get_movie_details(movie_title) {
    send_data_to_flask(movie_title);
}




input_box.onkeyup = (e) => {
    let movie_title = e.target.value;
    let suggestions_array = [];
    if (movie_title) {
        suggestions_array = movie_array.filter((data) => {
            return data.toLocaleLowerCase().startsWith(movie_title.toLocaleLowerCase());
        });
        suggestions_array = suggestions_array.map((data) => {
            return data = '<li>' + data + '</li>';
        });

        search_box.classList.add('active');  // Show autocomplete box.
        show_suggestions(suggestions_array);

        let all_list = suggestions_box.querySelectorAll('li');

        for (let i=0; i<all_list.length; i++) {
            all_list[i].setAttribute('onclick', 'select(this)');
        }
    } 
    else {
        search_box.classList.remove('active');  // Hide autocomplete box.
    }
}

function select(element) {
    let select_movie_title = element.textContent;
    input_box.value = select_movie_title;

    search_box.classList.remove('active');  // Hide autocomplete box.

    send_data_to_flask(select_movie_title);
}


function show_suggestions(suggestions_list) {
    let temp_list;
    if (!suggestions_list.length) {
        var movie_title = input_box.value;
        temp_list = '<li>' + movie_title + '</li>';
    }
    else {
        temp_list = suggestions_list.join('');
    }
    suggestions_box.innerHTML = temp_list;
}

