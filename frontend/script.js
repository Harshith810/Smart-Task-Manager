let historyOffset = 0;
let userId = localStorage.getItem("user_id");

if(!userId){
window.location.href = "login.html";
}

const API = "https://smart-task-manager-a5tm.onrender.com"

async function loadTasks(){

const res = await fetch(API + "/tasks?user_id=" + userId)
const tasks = await res.json()

const todayList = document.getElementById("todayTasks")
const yesterdayList = document.getElementById("yesterdayTasks")
const yesterdayTitle = document.getElementById("yesterdayTitle")

todayList.innerHTML = ""
yesterdayList.innerHTML = ""
yesterdayTitle.style.display = "none"

const today = new Date()
today.setHours(0,0,0,0)

const yesterday = new Date()
yesterday.setDate(today.getDate()-1)
yesterday.setHours(0,0,0,0)

tasks.forEach(task => {

const deadline = new Date(task.deadline)
const deadlineDay = new Date(task.deadline)

deadlineDay.setHours(0,0,0,0)

let targetList = null

if(deadlineDay.getTime() === today.getTime()){
targetList = todayList
}
else if(deadlineDay.getTime() === yesterday.getTime() && task.status === "pending"){
targetList = yesterdayList
yesterdayTitle.style.display = "block"
}
else{
return
}

const li = document.createElement("li")
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

targetList.appendChild(li)

})
}


async function addTask(){

const title = document.getElementById("title").value
const deadline = document.getElementById("deadline").value

if(!title || !deadline){
alert("Please enter task title and deadline")
return
}

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

const li = event.target.closest("li")

li.classList.add("delete-animation")

setTimeout(async () => {

await fetch(API + "/tasks/"+id,{
method:"DELETE"
})

loadTasks()

},300)

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
backgroundColor:["#00541f9e","#a30000"]
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

async function loadHistory(){

const res = await fetch(API + "/tasks?user_id=" + userId)
const tasks = await res.json()

const historySection = document.getElementById("history-section")
historySection.style.display="block"

window.scrollTo({
top: historySection.offsetTop - 120,
behavior: "smooth"
})

const list = document.getElementById("historyList")
list.innerHTML=""

tasks.sort((a,b)=> new Date(b.deadline) - new Date(a.deadline))

const groupedTasks = {}

tasks.forEach(task => {

const date = new Date(task.deadline)

const today = new Date()
const yesterday = new Date()
yesterday.setDate(today.getDate()-1)

let label = date.toDateString()

if(date.toDateString() === today.toDateString()){
label = "Today"
}
else if(date.toDateString() === yesterday.toDateString()){
label = "Yesterday"
}

if(!groupedTasks[label]){
groupedTasks[label] = []
}

groupedTasks[label].push(task)

})

Object.keys(groupedTasks).forEach(label => {

const header = document.createElement("h3")
header.textContent = label
header.style.marginTop = "20px"

list.appendChild(header)

groupedTasks[label].forEach(task => {

const li = document.createElement("li")

li.innerHTML = `
<div class="task-left">
<strong>${task.title}</strong>
<span>${new Date(task.deadline).toLocaleDateString()}</span>
<span class="status ${task.status}">${task.status}</span>
</div>

<div class="task-buttons">

<button onclick="editTask(${task.id}, '${task.deadline}')">
Edit
</button>

</div>
`

list.appendChild(li)

})

})

}

function prevDay(){
historyOffset++
loadHistory()
}

function nextDay(){
if(historyOffset > 0){
historyOffset--
}
loadHistory()
}


function logout(){

localStorage.removeItem("user_id")

window.location.href = "login.html"

}

async function moveToToday(id){

const today = new Date().toISOString()

await fetch(API + "/tasks/"+id,{
method:"PATCH",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
deadline: today
})
})

loadTasks()
loadHistory()

}

async function editTask(id, title, deadline){

const newTitle = prompt("Edit task title", title)

if(!newTitle) return

await fetch(API + "/tasks/"+id,{
method:"PATCH",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
title:newTitle
})
})

loadTasks()
loadHistory()

}

async function editTask(id, currentDeadline){

const action = prompt(
"Choose action:\n1 - Change Date\n2 - Delete Task"
)

if(action === "1"){

const newDate = prompt("Enter new date (YYYY-MM-DD)", currentDeadline)

if(!newDate) return

await fetch(API + "/tasks/"+id,{
method:"PATCH",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
deadline:newDate
})
})

}

else if(action === "2"){

const confirmDelete = confirm("Delete this task?")

if(!confirmDelete) return

await fetch(API + "/tasks/"+id,{
method:"DELETE"
})

}

loadTasks()
loadHistory()

}

document.getElementById("title").addEventListener("keypress", function(e){
if(e.key === "Enter"){
addTask()
}
})

loadTasks()
setInterval(loadTasks, 5000)
