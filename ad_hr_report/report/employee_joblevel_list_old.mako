<html>
	<head>
	<style>
			.no
			{
			text-align:center;
			padding:5px
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
		<h2 class="center">Employee List by Grade</h2>
	<% 
	dummy=False
	datalist=data['form']
	print "**********************",datalist
	%>
	<table class="data" border="1">
		<tr>
			<th class="block">No</th>
			<th class="block">NIK</th>
			<th class="block">Name</th>
			<th class="block">Department</th>
			<th class="block">Section</th>
			<th class="block">Admission</th>
			<th class="block">Admission Date</th>
			<th class="block">Job</th>
		</tr>
	<% no=1 %>
	%for level in get_job_level():
		<tr>
			<td colspan="10" style="padding:5px"><b>Grade : Level ${level.name}</b></td>
		</tr>
		<% employees=get_employee(datalist['active'],datalist['filter_dept'],datalist['filter_sect'],[level.id])%>
		%if employees>0:
			%for emp in employees:
				<tr>
					<td class="no" >${no}</td>
					<td class="no" >${emp.nik}</td>
					<td class="name">${emp.name}</td>
					<td class="nik">${emp.department_id.name}</td>
					<td class="nik">${emp.section.name}</td>
					<td class="nik">${emp.admission_letter}</td>
					<td class="no" >${emp.admission_date}</td>
					<td class="nik">${emp.job_id.name}</td>
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