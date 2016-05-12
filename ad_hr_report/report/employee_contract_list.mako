<html>
	<head>
	<style>
		.break { page-break-after: always; }
			
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
	<h2 class="center">Employee Contract List</h2>
	<% 
	dummy=False
	datalist=data['form']
	%>
	<table class="data" border="1">
		<tr>
			<th class="block">No</th>
			<th class="block">NIK</th>
			<th class="block">Name</th>
			<th class="block">Admission</th>
			<th class="block">Level</th>
			<th class="block">Basic Wage</th>
			<th class="block">Allowance</th>
			<th class="block">DPLK</th>
		</tr>
	<% no=1 %>
	<!--%for dep in get_dept(datalist['filter_dept']):   -->
		<tr>
			<td colspan="10" style="padding:5px"><b>Departemen :${dep.name}</b></td>
		</tr>
	<!--	<% sections=get_section(dep.id,datalist['filter_sect']) %> -->
		%if len(sections)>0 and sections:
			%for section in sections:
				<tr>
					<td colspan="1"></td>
					<td colspan="7" style="padding:5px"><b>Section : ${section.name}</b></td>
				</tr>

				<% employees=get_employee(datalist['active'],[dep.id],[section.id])%>
				%if employees>0:
					%for emp in employees:
						<tr>
							<td class="no" >${no}</td>
							<td class="no" >${emp.nik}</td>
							<td class="name">${emp.name}</td>
							<td class="nik">${emp.admission_letter}</td>
							<td class="nik">${emp.job_id.name}</td>
							<td class="no" >${emp.current_job_level.name}</td>
							<td class="age">${emp.work_location.title()}</td>
						</tr>
						<% no+=1 %>
					%endfor
				%else:
					<tr>
						<td colspan="10" align="center">No Employee defined in this section</td>
					</tr>
				%endif
				<tr><td colspan="10">&nbsp;</td></tr>
			%endfor
		%else:
				<% employees=get_employee(datalist['active'],[dep.id])%>
				%if employees>0:
					%for emp in employees:
						<tr>
							<td class="no">${no}</td>
							<td class="no">${emp.nik}</td>
							<td class="name">${emp.name}</td>
							<td class="nik">${emp.admission_letter}</td>
							<td class="no" >${emp.admission_date}</td>
							<td class="nik">${emp.job_id.name}</td>
							<td class="no" >${emp.current_job_level.name}</td>
							<td class="nik">${emp.work_location}</td>
						</tr>
						<% no+=1 %>
					%endfor
				%else:
					<tr>
						<td colspan="10" align="center">No Employee defined in this section</td>
					</tr>
				%endif
			<tr><td colspan="10">&nbsp;</td></tr>
		%endif			
	</table>
	<p style="page-break-after:always"></p>
	</body>
</html>