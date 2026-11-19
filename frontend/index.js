    const API = "https://vistet94k4.execute-api.us-west-2.amazonaws.com/uploads";
    const LOGIN_URL = "https://sharingan-ai-anmol-26.auth.us-west-2.amazoncognito.com/login?client_id=5b1gnt1p17h5ve1rk83g0k0uks&response_type=token&scope=email+openid&redirect_uri=https://d2sjhbw2mydv2l.cloudfront.net";


    //saving token
    if(location.hash.includes("id_token=")){
        const urlData = new URLSearchParams(location.hash.slice(1));
        localStorage.setItem("token_id", urlData.get("id_token"));
        location.hash = "";
    }

    //getting token
    const token = localStorage.getItem("token_id");
    if(token){
        document.getElementById("login-btn").classList.add("hidden");
        document.getElementById("logout-btn").classList.remove("hidden");
    }


    //login/logout buttons
    document.getElementById("login-btn").onclick = () => location.href = LOGIN_URL;
    document.getElementById("logout-btn").onclick = () => {
        localStorage.removeItem("token_id");
        location.reload();
    }

    //select image button
    const fileInput = document.getElementById("file");
    const selectBtn = document.getElementById("select-btn");
    selectBtn.onclick = () => fileInput.click();
    fileInput.onchange = () => {
        selectBtn.textContent = fileInput.files[0] ? fileInput.files[0].name : "Select Image";
    }


    document.getElementById("btn-upload").onclick = async() => {
        const file = fileInput.files[0];
        const status = document.getElementById("status");
        if(!token){
            status.className = "status error";
            status.textContent = "Please Login first";
            return;
        }
        if(!file) {
            status.className = "status error";
            status.textContent = "Pick a file first";
            return;
        }

        const headers = {Authorization: "Bearer " + token};

        status.className = "status";
        status.innerHTML = `<div class="spinner"></div> Uploading...`;
        const res = await fetch(API, {method:"POST", headers});
        if (!res.ok){
            status.className = "status error";
            status.textContent = "Upload failed";
            return;
        }
        const {image_id, upload_url} = await res.json();

        status.innerHTML = `<div class="spinner"></div> Uploading to S3...`;
        const put = await fetch(upload_url, {
            method: "PUT",
            body: file
        })

        if(put.ok){
            status.innerHTML = `<div class="spinner"></div> Uploaded! Waiting for Ai worker...`;

          for (let i=0; i<10;i++){
            await new Promise((resolve) => setTimeout(resolve, 2000));

            const res = await fetch(`${API}/${image_id}`, {headers})
            const data = await res.json();

            if(data.status == "Done"){
                status.className = "status result";
                status.textContent = `Your character is ${data.character_name}`;
                return;
            }
            status.innerHTML = `<div class="spinner"></div> Looking for a character...`;
            }
            status.className = "status error";
            status.textContent = "Character not found.";

        } else{
            status.className = "status error";
            status.textContent = "Upload failed";
        }
    }