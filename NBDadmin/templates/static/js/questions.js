function visible_block_main (id) {
    $('#hiden_box_m'+id).toggleClass('box-activ');
  };

function visible_block_f (id) {
    $('#hiden_box_f'+id).toggleClass('box-activ');
  };

function visible_block_s (id) {
    $('#hiden_box_s'+id).toggleClass('box-activ');
  };

var counter = 1;

function edit_stat_ques(id) {
    $.ajax({
        type: "GET",
        url:"/questions/edit/stat/" + id,
        context: document.body,
        success(data) {
            $("#stat_block"+id).after(data);
            $('#popup-bg_edit').fadeIn(600);
        }
    });
  }

function edit_main_ques(id) {
    $.ajax({
        type: "GET",
        url:"/questions/edit/main/" + id,
        context: document.body,
        success(data) {
            $("#main_block"+id).after(data);
            $('#popup-bg').fadeIn(600);
        }
    });
  }

function edit_main_ans(id) {
    $.ajax({
        type: "GET",
        url: "/questions/edit/answer/main/" + id,
        context: document.body,
        success(data) {
            $("#main_answer"+id).after(data);
            $('#popup-bg').fadeIn(600);
        }
    });
}

function new_main_ques() {
    $.ajax({
        type: "GET",
        url:"/questions/new/main/",
        context: document.body,
        success(data) {
            $("#main_block").prepend(data);
            $('#popup-bg_add').fadeIn(600);
        }
    });
  }

function new_stat_ques() {
    $.ajax({
        type: "GET",
        url:"/questions/new/stat/",
        context: document.body,
        success(data) {
            $("#stat_block").prepend(data);
            $('#popup-bg_add').fadeIn(600);
        }
    });
  }

function cancel_popup_ques() {
    $(".popup-bg-ques").remove();
    counter = 1;
}
function cancel_popup() {
    $(".popup-bg").remove();
    counter = 1;
}

function add_answer_main(id) {
    $.ajax({
        type: "GET",
        url: "/questions/newanswer/main/" + id,
        context: document.body,
        success(data) {
          $("#answer_main").append(data);     
          $('#popup-bg').fadeIn(600);
        }       
    })
}


function add_answer_main_in_new_ques() {
    $.ajax({
        type: "GET",
        url: "/questions/newanswer/main/newques/" + ++counter,
        context: document.body,
        success(data) {
          $("#new_main_add_answer").append(data);     
        }       
    })
}

function add_answer_f_s(count) {
    $.ajax({
        type: "GET",
        url: "/questions/newanswer/fs/" + (Number(count) + counter++),
        context: document.body,
        success(data) {
          $("#answerFS").append(data);
        }
    })
}

function add_answer_to_answer_f_s(count) {
    $.ajax({
        type: "GET",
        url: "/questions/newanswertoanswer/fs/" + (Number(count) + counter++),
        context: document.body,
        success(data) {
          $("#ans_to_ans").append(data);
        }
    })
}

function alertDeleteQuesMain (id) {
        var del = confirm("Вы уверены, что хотите удалить вопрос?");
        if (del) {
          $.ajax({
            url:"/questions/delete/main/",
            type: 'POST',
            data: {"id":`${id}`},
            statusCode: {
                200: function() {
                    $("#main_block" + id).remove();
                    alert("Успешно удалено");
                }
            }
        });
        } else {
        }
        } 

function alertDeleteAns (id) {
        var del = confirm("Вы уверены, что хотите удалить ответ?");
        if (del) {
          $.ajax({
            url:"/questions/delete/answer/main/",
            type: 'POST',
            data: {"id":`${id}`},
            statusCode: {
                200: function() {
                    $("#main_answer" + id).remove();
                    alert("Успешно удалено");
                }
            }
        });
        } else {
        }
        } 

function postMainQues (id) {
    if (document.getElementById('editMainQues').value.trim() === '') { return }
    let form = $("#main_question")
    $.ajax({
        url: '/questions/addedit/main/' + id,
        type: 'POST',
        data: form.serialize(),
        statusCode: {
            200: function(data) {
                let ques = $('#main_block' + id)
                ques.after(data);
                ques.remove();
                $(".popup-bg").remove();
            }
        }
    })
}

function postMainAnswer (id) {
    if (document.getElementById('editMainAnswer').value.trim() === '') { return }
    if (document.getElementById('editMainAnswerToAnswer').value.trim() === '') { return }
    let form = $("#main_answer")
    $.ajax({
        url: '/questions/addedit/main/answer/' + id,
        type: 'POST',
        data: form.serialize(),
        statusCode: {
            200: function(data) {
                let ans = document.getElementById('main_answer' + id);
                let ques = document.getElementById(ans.offsetParent.id);
                let ques2 = $('#'+ques.parentElement.id)
                ques2.after(data);
                ques2.remove();
                $(".popup-bg").remove();
            }
        }
    })
}

function createMainAnswer (id) {
    if (document.getElementById('addAnswerMain').value.trim() === '') { return }
    if (document.getElementById('AAMintellect').value.trim() === '') { return }
    if (document.getElementById('AAMphys').value.trim() === '') { return }
    if (document.getElementById('AAMskill').value.trim() === '') { return }
    if (document.getElementById('addAnswerToAnswerMain').value.trim() === '') { return }
    let form = $('#main_answer')
    $.ajax({
        url: '/questions/add/main/answer/'+ id,
        type: 'POST',
        data: form.serialize(),
        statusCode: {
            200: function(data) {
                let ques = $('#main_block' + id)
                ques.after(data);
                ques.remove();
                $(".popup-bg").remove();
            }
        }
    })
}

function createMainQues () {
    let form = $('#main_ques')
    $.ajax({
        url: '/questions/create/main/',
        type: 'POST',
        data: form.serialize(),
        statusCode: {
            200: function(data) {
                $('#main_block').append(data);
                counter = 1;
                $(".popup-bg-ques").remove();
            }
        }
    })
}

function deleteAnsInNewQues (count) {
    $('#newAnswer' + count).remove();
}

function editFilterQues (id) {
    $.ajax({
        url: '/questions/edit/filter/' + id,
        type: 'GET',
        context: document.body,
        success(data) {
                $("#filter_block").after(data);
                $('#popup-bg').fadeIn(600);
        }
    })
}

function saveFilterQues (id) {
    if (document.getElementById('EFquestion').value.trim() === '') { return }
    let form = $('#filterQues')
    $.ajax({
        url: '/questions/addedit/filter/' + id,
        type: 'POST',
        data: form.serialize(),
        success(data) {
            let ans = $('#filter_block' + id);
            ans.after(data);
            ans.remove();
            $(".popup-bg").remove();
        }
    })
}

function deleteFilterAnswer (count) {
    $(`#answer${count}`).remove();
}

function deleteFilterAnswerToAnswer (count) {
    $(`#answer_to_answer${count}`).remove();
}

function editFilterAnswer (id) {
    $.ajax({
        url: '/questions/edit/answer/filter/' + id,
        type: 'GET',
        context: document.body,
        success(data) {
                $("#filter_block").after(data);
                $('#popup-bg').fadeIn(600);
        }
    })
}

function saveFilterAnswer (id) {
    let form = $('#answer')
    $.ajax({
        url: '/questions/addedit/filter/answer/' + id,
        type: 'POST',
        data: form.serialize(),
        statusCode: {
            200: function(data) {
                let ans = $('#filter_block' + id);
                ans.after(data);
                ans.remove();
                $(".popup-bg-ques").remove();
        },
            400: function(data) {
                alert("Заполните все поля!")
            }
        }
    })
}

function editFilterAnswerToAnswer (id) {
    $.ajax({
        url: '/questions/edit/answertoanswer/filter/' + id,
        type: 'GET',
        context: document.body,
        success(data) {
                $("#filter_block").after(data);
                $('#popup-bg').fadeIn(600);
        }
    })
}

function saveFilterAnswerToAnswer (id) {
    if (document.getElementById('addAnswerMain').value.trim() === '') { return }
    if (document.getElementById('addAnswerMain').value.trim() === '') { return }
    let form = $('#answer')
    $.ajax({
        url: "/questions/addedit/filter/answertoanswer/" + id,
        type: 'POST',
        data: form.serialize(),
        success(data) {
            let ans = $('#filter_block' + id);
            ans.after(data);
            ans.remove();
            $(".popup-bg-ques").remove();
        }
    })
}              
                
function newFilterQues() {
    $.ajax({
        type: "GET",
        url:"/questions/new/filter/",
        context: document.body,
        success(data) {
            $("#filter_block").prepend(data);
            $('#popup-bg_add').fadeIn(600);
        }
    });
  }

function newFilter () {
    if (document.getElementById('NFques').value.trim() === '') { return }
    if (document.getElementById('NFanswer').value.trim() === '') { return }
    if (document.getElementById('NFanswerToAnswer').value.trim() === '') { return }
    let form = $('#newFilter')
    $.ajax({
        url: '/questions/create/filter/',
        type: 'POST',
        data: form.serialize(),
        statusCode: {
            200: function(data) {
                $('#filter_block').append(data);
                $('#popup-bg_add').remove();
            },
            400: function(data) {
                alert("Заполните все поля!")
            }
        }
    })
}


function alertDeleteQuesFilter (id) {
    var del = confirm("Вы уверены, что хотите удалить вопрос?");
    if (del) {
      $.ajax({
        url:"/questions/delete/filter/",
        type: 'POST',
        data: {"id":`${id}`},
        statusCode: {
            200: function() {
                $("#filter_block" + id).remove();
                alert("Успешно удалено");
            }
        }
    });
    } else {
    }
    } 

function editStatQues (id) {
    $.ajax({
        url: '/questions/edit/stat/' + id,
        type: 'GET',
        context: document.body,
        success(data) {
                $("#stat_block").after(data);
                $('#popup-bg').fadeIn(600);
        }
    })
}

function saveStatQues (id) {
    if (document.getElementById('ESquestion').value.trim() === '') { return }
    let form = $('#statQues')
    $.ajax({
        url: '/questions/addedit/stat/' + id,
        type: 'POST',
        data: form.serialize(),
        success(data) {
            let ans = $('#stat_block' + id);
            ans.after(data);
            ans.remove();
            $(".popup-bg").remove();
        }
    })
}

function editStatAnswer (id) {
    $.ajax({
        url: '/questions/edit/answer/stat/' + id,
        type: 'GET',
        context: document.body,
        success(data) {
                $("#stat_block").after(data);
                $(".popup-bg-ques").fadeIn(600);
        }
    })
}

function saveStatAnswer (id) {
    let form = $('#answer')
    $.ajax({
        url: '/questions/addedit/stat/answer/' + id,
        type: 'POST',
        data: form.serialize(),
        statusCode: {
            200: function(data) {
                let ans = $('#stat_block' + id);
                ans.after(data);
                ans.remove();
                $(".popup-bg-ques").remove();
            },
            400: function(data) {
                alert("Заполните все поля!")
            }
        }
    })
}

function editStatAnswerToAnswer (id) {
    $.ajax({
        url: '/questions/edit/answertoanswer/stat/' + id,
        type: 'GET',
        context: document.body,
        success(data) {
                $("#stat_block").after(data);
                $('#popup-bg').fadeIn(600);
        }
    })
}

function saveStatAnswerToAnswer (id) {
    let form = $('#answer')
    $.ajax({
        url: "/questions/addedit/stat/answertoanswer/" + id,
        type: 'POST',
        data: form.serialize(),
        statusCode: {
            200: function(data) {
                let ans = $('#stat_block' + id);
                ans.after(data);
                ans.remove();
                $(".popup-bg-ques").remove();
            },
            400: function(data) {
                alert("Заполните все поля!")
            }
        }
    })
}              
                
function newStatQues() {
    $.ajax({
        type: "GET",
        url:"/questions/new/stat/",
        context: document.body,
        success(data) {
            $("#stat_block").prepend(data);
            $('#popup-bg-ques').fadeIn(600);
        }
    });
  }

function newStat () {
    let form = $('#newStat')
    $.ajax({
        url: '/questions/create/stat/',
        type: 'POST',
        data: form.serialize(),
        statusCode: {
            200: function(data) {
                $('#stat_block').append(data);
                $(".popup-bg-ques").remove();
            },
            400: function(data) {
                alert("Заполните все поля!")
            }
        }
    })
}

function alertDeleteQuesStat (id) {
    var del = confirm("Вы уверены, что хотите удалить вопрос?");
    if (del) {
      $.ajax({
        url:"/questions/delete/stat/",
        type: 'POST',
        data: {"id":`${id}`},
        statusCode: {
            200: function() {
                $("#stat_block" + id).remove();
                alert("Успешно удалено");
            }
        }
    });
    } else {
    }
    } 
