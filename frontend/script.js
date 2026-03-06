let userId = localStorage.getItem("user_id");

if(!userId){
    window.location.href = "login.html";
}

const API = "https://smart-task-manager-a5tm.onrender.com"

async function loadTasks() {

const res = await fetch(API + "/tasks?user_id=" + userId)
const tasks = await res.json()

const list = document.getElementById("taskList")
list.innerHTML = ""

tasks.forEach(task => {

const li = document.createElement("li")
const deadline = new Date(task.deadline)
const now = new Date()

if(task.status === "pending" && deadline < now){
li.classList.add("overdue")
}

li.innerHTML = `
<div class="task-left">
<strong>${task.title}</strong>
<span class="status ${task.status}">${task.status}</span>
<span class="reschedule">Reschedules: ${task.reschedule_count}</span>
</div>

<div class="task-buttons">
<button class="complete-btn" onclick="completeTask(${task.id})">
<i class="fa-solid fa-check"></i> Complete
</button>

<button class="delete-btn" onclick="deleteTask(${task.id})">
<i class="fa-solid fa-trash"></i> Delete
</button>
</div>
`

list.appendChild(li)

})
}

async function addTask(){

const title = document.getElementById("title").value
const deadline = document.getElementById("deadline").value

await fetch(API + "/tasks",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
title,
deadline,
user_id:userId
})
})

document.getElementById("title").value = ""
document.getElementById("deadline").value = ""

loadTasks()

}

async function completeTask(id){

await fetch(API + "/tasks/"+id+"/complete",{
method:"PATCH"
})

confetti({
particleCount:120,
spread:70,
origin:{y:0.6}
})

loadTasks()

}

async function deleteTask(id){

await fetch(API + "/tasks/"+id,{
method:"DELETE"
})

loadTasks()

}

async function loadAnalytics(){

const res = await fetch(API + "/analytics")
const data = await res.json()

document.getElementById("analytics").innerHTML =
`Total Tasks: ${data.total_tasks}<br>
Completion Rate: ${data.completion_rate}`

const ctx = document.getElementById("analyticsChart")

new Chart(ctx,{
type:"doughnut",
data:{
labels:["Completed","Pending"],
datasets:[{
data:[data.completed_tasks,data.pending_tasks],
backgroundColor:["#64f1984e","#a30000"]
}]
},
options:{
responsive:false,
plugins:{
legend:{
position:"bottom"
}
}
}
})

}

loadTasks()
setInterval(loadTasks, 5000)
