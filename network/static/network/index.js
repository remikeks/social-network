document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.edit').forEach(button => {
        button.onclick = function() {
            // Get the button id which corresponds to the post id
            const id = this.id;

            // Send a GET request to the application's API to retrieve the post
            fetch(`/post/${id}`)
            .then(response => response.json())
            .then(post => {
                console.log(post);

                // Provide a form for editing post content
                document.querySelector(`#content${id}`).innerHTML = `<form id="form${id}">
                                                                    <textarea id="edited${id}">${post.content}</textarea>
                                                                    <input id="submit${id}" type="submit" value="Save Edit">
                                                                    </form>`
                this.style.display = "none";

                document.querySelector(`#form${id}`).onsubmit = function() {

                    // Send a POST request to the API to update the content field of the post
                    fetch(`/post/${id}`, {
                        method: 'POST',
                        body: JSON.stringify({
                            content: document.querySelector(`#edited${id}`).value
                        })
                    })
                    .then(response => response.json())
                    .then(edit => {
                        console.log(edit);
                        document.querySelector(`#content${id}`).innerHTML = edit.content;
                        button.style.display = "block";
                    })              
                return false;
                }
            })
        }
    })


   document.querySelectorAll('.like').forEach(button => {
        button.onclick = function() {
            // Extract the post id from the button; this id will then be used in the call to fetch
            const id = parseInt(this.id.slice(4));

            // Retrieve the post
            fetch(`/post/${id}`)
            .then(response => response.json())
            .then(() => {
                    // Send a POST request and update both the likes count and button text
                    fetch(`/like/${id}`, {
                        method: 'POST',
                      })
                      .then(response => response.json())
                      .then(data => {
                        document.querySelector(`#like${id}`).innerHTML = data.likes;
                        this.textContent = data.buttonText;
                      })
                    })
            return false;
        }
    })


    document.querySelectorAll('.follow').forEach(button => {
        button.onclick = function() {
            // Get the user id from the button; this id will be used in the call to fetch
            const id = parseInt(this.id);
            const follower_count = document.querySelector(`#followers${id}`);

            fetch(`/follow/${id}`, {
                method: 'POST',
              })
              .then(response => response.json())
              .then(data => {
                console.log(data);
                this.textContent = data.buttonText;
                follower_count.innerHTML = data.followers;
              })
        }
    })

})