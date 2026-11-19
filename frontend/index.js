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
        document.getElementById("auth-status").textContent = "Logged in! You can upload images now.";
    }


    //login/logout buttons
    document.getElementById("login-btn").onclick = () => location.href = LOGIN_URL;
    document.getElementById("logout-btn").onclick = () => {
        localStorage.removeItem("token_id");
        location.reload();
    }


    document.getElementById("btn-upload").onclick = async() => {
        const file = document.getElementById("file").files[0];
        const status = document.getElementById("status");
        if(!token){
            status.textContent = "Please Login first";
            return;
        }
        if(!file) {
            status.textContent = "Pick a file first";
            return;
        }

        const headers = {Authorization: "Bearer " + token};

        status.textContent = "Uploading..."
        const res = await fetch(API, {method:"POST", headers});
        if (!res.ok){
            status.textContent = "Upload failed";
            return;
        }
        const {image_id, upload_url} = await res.json();

        status.textContent = "Uploading to S3..."
        const put = await fetch(upload_url, {
            method: "PUT",
            body: file
        })

        if(put.ok){
            status.textContent = `Uploaded! Waiting for Ai worker...` 

          for (let i=0; i<10;i++){
            await new Promise((resolve) => setTimeout(resolve, 2000));

            const res = await fetch(`${API}/${image_id}`, {headers})
            const data = await res.json();

            if(data.status == "Done"){
                status.textContent = `
                Your character is ${data.character_name}
                `
                return;
            }
            status.textContent = "Looking for a character..." 
            }
            status.textContent = "Character not found.";

        } else{
            status.textContent = "Upload failed";
        }
    }
