<html>
	<head>
	<style>
		    .no
			{
			text-align:center;
			padding:5px;
			}
			
			table
			{
			padding:10px;
			border-collapse:collapse;
			border: black solid thin;
			}
			
			table.data
			{
			padding:10px;
			border: 1px black solid thin;
			width:100%;
			
			}
			.block
			{
			background-color:black;
			color:white;
			font-weight:bold;
			}
			
			th
			{
			padding:5px;
			border-collapse:collapse;
			border: black solid thin;
			}
			
			.bold
			{
			font-weight:bold;
			}
			
			.padded
			{
			padding-top:8px;
			}
			
			.td
			{
			text-align:center;
			padding-bottom:80px;
			width:50%;
			font-size:11pt;
			}
			
			.nama
			{
			padding-top:80px;
			text-align:center;
			width:50%;
			font-weight:bold;
			}
			
			.center
			{
			text-align:center;
			vertical-align:center;
			}
			
			.sum
			{
			background-color:black;
			color:white;
			font-weight:bold;
			}
			
			.total
			{
			border-top:black solid thin;
			}
	</style>
	</head>
	<body>
	<center><h2>Employee List by Work Location</h2></center>
	<% 
	dummy=False
	datalist=data['form']
	%>
	<table class="data" border="1">
		<tr>
			<th class="block" >No</th>
			<th class="block" >NIK</th>
			<th class="block" >Name</th>
			<th class="block" >Office</th>
			<th class="block" >Department</th>
			<th class="block" >Section</th>
			<th class="block" >Job</th>
		</tr>
	<% no=1 %>
	%for work_location in get_work_location():
		<tr>
			<td colspan="10" style="padding:5px"><b>Work Location : ${work_location.upper()}</b></td>
		</tr>
		<% employees=get_employee(datalist['active'],datalist['filter_dept'],datalist['filter_sect'],dummy,[work_location],dummy)%>
		%if employees>0:
			%for emp in employees:
				<tr>
					<td class="no">${no}</td>
					<td class="no"> ${emp.nik}</td>
					<td class="nik"> ${emp.name}</td>
					<td class="no"> ${emp.type.upper()}</td>
					<td class="nik"> ${emp.department_id.name}</td>
					<td class="nik"> ${emp.section.name}</td>
					<td class="nik"> ${emp.job_id.name}</td>
				</tr>
				<% no+=1 %>
			%endfor
		%else:
			<tr>
				<td colspan="10" align="center">No Employee defined in this section</td>
			</tr>
		%endif
	%endfor
	</table>
	<p style="page-break-after:always"></p>
	</body>
</html>