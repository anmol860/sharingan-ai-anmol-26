    const API = "https://vistet94k4.execute-api.us-west-2.amazonaws.com/uploads";

    document.getElementById("btn-upload").onclick = async() => {
        const file = document.getElementById("file").files[0];
        const status = document.getElementById("status");
        if(!file) {
            status.textContent = "Pick a file first";
            return;
        }

        status.textContent = "Uploading..."
        const res = await fetch(API, {method:"POST"});
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

            const res = await fetch(`${API}/${image_id}`)
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
