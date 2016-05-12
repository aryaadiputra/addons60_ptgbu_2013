<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
	<head>
		<style>
			body
			{
			font-size:10px;
			}
		
			.level1
			{
			font-weight:bold;
			font-size:16px;	
			}
			
			th
			{
			background-color:grey;
			}
			
			.total
			{
			background-color:grey;
			font-weight:bold;
			}
			
			.break { page-break-after: always; }
		</style>
	</head>
	<body width="100%">
		<% setLang(company.partner_id.lang) %>
		<table width="100% cellpadding="3">
			<tr>
				<td align="left" style="font-size:8px;">${ time.strftime("%r") },  ${ time.strftime("%d %B %Y") }</td>
			</tr>
		</table>
		%for o in get_object(data):
			%for dept in get_department(o.dept_relation2):
				<table width="100%" class="break">
					<tr>
						<td>
							<table>
								<tr>
								%if o.cut_date:
									<td class="level1" colspan="2">Budget Reporting: ${time.strftime('%d %b %Y', time.strptime(o.cut_date,'%Y-%m-%d'))}</td>
								%else:
									<td class="level1" colspan="2">Budget Reporting: ${time.strftime('%b %Y', time.strptime(o.period_id.date_start,'%Y-%m-%d'))}</td>
								%endif
								</tr>
								<tr>
									<td class="level1">for year ended</td>
									%if o.period_id:
										<td class="level1">: ${o.period_id.name[0:4]}</td>
									%else:
										<td class="level1">: -</td>
									%endif
								</tr>
								<tr>
									<td class="level1">Division</td>
									<td class="level1">: ${dept.division_id.name or "-"}</td>
								</tr>
								<tr>
									<td class="level1">Department</td>
									<td class="level1">: ${dept.name or "-"}</td>
								</tr>
								<tr>
									<td class="level1" colspan="2">in IDR</td>
								</tr>
							</table>
						</td>
					</tr>
					<tr>
						<td colspan="2">
							<table width="100%">
								<tr>
									<th colspan="2" rowspan="3">Description</th>
									<th colspan="1" rowspan="2">Actual Previous Year</th>
									<th colspan="2" rowspan="1">Actual Current Year</th>
									<th colspan="2" rowspan="1">Budget Current Year</th>
									<th colspan="4" rowspan="1">(over) - under</th>
									<th colspan="2" rowspan="1">vs Total Budget Dept.</th>
								</tr>
								<tr>
									<th colspan="1" rowspan="1">Month</th>
									<th colspan="1" rowspan="1">Ytd</th>
				
									<th colspan="1" rowspan="1">Month</th>
									<th colspan="1" rowspan="1">Ytd</th>
				
									<th colspan="2" rowspan="1">Monthly</th>
									<th colspan="2" rowspan="1">Ytd</th>
				
									<th colspan="1" rowspan="2">Amt</th>
									<th colspan="1" rowspan="2">% remaining</th>
								</tr>
								<tr>
									<th colspan="1" rowspan="1">Amt</th>
				
									<th colspan="1" rowspan="1">Amt</th>
									<th colspan="1" rowspan="1">Amt</th>
				
									<th colspan="1" rowspan="1">Amt</th>
									<th colspan="1" rowspan="1">Amt</th>
				
									<th colspan="1" rowspan="1">Amt</th>
									<th colspan="1" rowspan="1">%</th>
									<th colspan="1" rowspan="1">Amt</th>
									<th colspan="1" rowspan="1">%</th>
								</tr>
							%for selected in data['form'].get('budget_item2', False):
								<%sum_act_last_year,sum_act_current,sum_act_ytd,sum_bgt_monthly,sum_bgt_ytd,sum_act_sum,sum_act_ytd_sum,sum_bgt_year=0,0,0,0,0,0,0,0%>
								%for item in get_line(data,dept,selected):
									<tr>
									%if item.type=='view':
										<td colspan="2"><span>${ '&nbsp;&nbsp;&nbsp;&nbsp;'*(item.level) }</span><b>${item.name}</b></td>
										<td colspan="1" style="text-align:right">${formatLang(compute_view(data, dept,item,o.period_id,o.cut_date)['balance_last_year'], digits=get_digits(dp='Budget'))}</td>
										<td colspan="1" style="text-align:right">${formatLang(compute_view(data, dept,item,o.period_id,o.cut_date)['act_monthly'], digits=get_digits(dp='Budget'))}</td>
										<%act_ytd_view		= compute_view(data, dept,item,o.period_id,o.cut_date)['act_ytd']%>
										<td colspan="1" style="text-align:right">${formatLang(act_ytd_view, digits=get_digits(dp='Budget'))}</td>
										<%bgt_monthly_view	= compute_view(data, dept,item,o.period_id,o.cut_date)['bgt_monthly']%>
										<td colspan="1" style="text-align:right">${formatLang(bgt_monthly_view, digits=get_digits(dp='Budget'))}</td>
										<%bgt_yearly_view	= compute_view(data, dept,item,o.period_id,o.cut_date)['bgt_yearly']%>
										<td colspan="1" style="text-align:right">${formatLang(bgt_yearly_view, digits=get_digits(dp='Budget'))}</td>
										<%rem_monthly_view	= compute_view(data, dept,item,o.period_id,o.cut_date)['rem_monthly']%>
										<td colspan="1" style="text-align:right">${formatLang(rem_monthly_view, digits=get_digits(dp='Budget'))}</td>
										<td colspan="1" style="text-align:right">${"%.2f" %(100*(rem_monthly_view/bgt_monthly_view))}</td>
										<%rem_ytd_view		= compute_view(data, dept,item,o.period_id,o.cut_date)['rem_ytd']%>
										<td colspan="1" style="text-align:right">${formatLang(rem_ytd_view, digits=get_digits(dp='Budget'))}</td>
										<td colspan="1" style="text-align:right">${"%.2f" %(100*(rem_ytd_view/bgt_yearly_view))}</td>
										<%bgt_year_view		= compute_view(data, dept,item,o.period_id,o.cut_date)['bgt_year']%>
										<td colspan="1" style="text-align:right">${formatLang(bgt_year_view, digits=get_digits(dp='Budget'))}</td>
										<td colspan="1" style="text-align:right">${"%.2f" %(100*((bgt_year_view-act_ytd_view)/bgt_year_view))}</td>
									%else:
										<td colspan="2"><span>${ '&nbsp;&nbsp;&nbsp;&nbsp;'*(item.level) }</span>- ${item.name}</td>
											<%act_last_year	= compute_lastyear_real_sum(item,o.period_id, dept)['balance_real']%>
										<td colspan="1" style="text-align:right">${formatLang(act_last_year, digits=get_digits(dp='Budget'))}</td>
											<%act_current	= compute_real_sum(item,o.period_id,o.cut_date,dept)['balance_real']%>
										<td colspan="1" style="text-align:right">${formatLang(act_current, digits=get_digits(dp='Budget'))}</td>
											<%act_ytd		= compute_ytd_real_sum(item,o.period_id,o.cut_date, dept)['balance_real']%>
										<td colspan="1" style="text-align:right">${formatLang(act_ytd, digits=get_digits(dp='Budget'))}</td>
											<%bgt_monthly	= get_budget(item,o.period_id,dept)['monthly']%>
										<td colspan="1" style="text-align:right">${formatLang(bgt_monthly, digits=get_digits(dp='Budget'))}</td>
											<%bgt_ytd		= get_budget(item,o.period_id,dept)['yearly']%>
										<td colspan="1" style="text-align:right">${formatLang(bgt_ytd, digits=get_digits(dp='Budget'))}</td>
											<%act_sum		= compute_real_sum(item,o.period_id,o.cut_date,dept)['balance']%>
										<td colspan="1" style="text-align:right">${formatLang(act_sum, digits=get_digits(dp='Budget'))}</td>
										<td colspan="1" style="text-align:right">${compute_real_sum(item,o.period_id,o.cut_date,dept)['percent']}</td>
											<%act_ytd_sum	= compute_ytd_real_sum(item,o.period_id,o.cut_date, dept)['balance']%>
										<td colspan="1" style="text-align:right">${formatLang(act_ytd_sum, digits=get_digits(dp='Budget'))}</td>
										<td colspan="1" style="text-align:right">${compute_ytd_real_sum(item,o.period_id,o.cut_date,dept)['percent']}</td>
											<%bgt_year		= get_budget(item,o.period_id,dept)['year']%>
										<td colspan="1" style="text-align:right">${formatLang(bgt_year, digits=get_digits(dp='Budget'))}</td>
										<td colspan="1" style="text-align:right">${"%.2f" %(100*((bgt_year-act_ytd)/bgt_year))}</td>
										<td colspan="1"></td>
										<%sum_act_last_year	+= act_last_year	%>
										<%sum_act_current	+= act_current		%>
										<%sum_act_ytd		+= act_ytd			%>
										<%sum_bgt_monthly	+= bgt_monthly		%>
										<%sum_bgt_ytd		+= bgt_ytd			%>
										<%sum_act_sum		+= act_sum			%>
										<%sum_act_ytd_sum	+= act_ytd_sum		%>
										<%sum_bgt_year		+= bgt_year			%>
									%endif
									</tr>
								%endfor
								</tr>
									<td class="total" colspan="2" style="text-align:left">TOTAL ${get_period_name(selected).name or "-"}</td>
									<td class="total" colspan="1" style="text-align:right">${formatLang(sum_act_last_year, digits=get_digits(dp='Budget'))}</td>
									<td class="total" colspan="1" style="text-align:right">${formatLang(sum_act_current, digits=get_digits(dp='Budget'))}</td>
									<td class="total" colspan="1" style="text-align:right">${formatLang(sum_act_ytd, digits=get_digits(dp='Budget'))}</td>
									<td class="total" colspan="1" style="text-align:right">${formatLang(sum_bgt_monthly, digits=get_digits(dp='Budget'))}</td>
									<td class="total" colspan="1" style="text-align:right">${formatLang(sum_bgt_ytd, digits=get_digits(dp='Budget'))}</td>
									<td class="total" colspan="1" style="text-align:right">${formatLang(sum_act_sum, digits=get_digits(dp='Budget'))}</td>

									%if sum_bgt_monthly==0:
									<td class="total" colspan="1" style="text-align:right">${"%.2f" %(0)}</td>
									%else:
									<td class="total" colspan="1" style="text-align:right">${"%.2f" %(100*(sum_act_sum/sum_bgt_monthly))}</td>
									%endif

									<td class="total" colspan="1" style="text-align:right">${formatLang(sum_act_ytd_sum, digits=get_digits(dp='Budget'))}</td>

									%if sum_bgt_ytd==0:
									<td class="total" colspan="1" style="text-align:right">${"%.2f" %(0)}</td>
									%else:
									<td class="total" colspan="1" style="text-align:right">${"%.2f" %(100*(sum_act_ytd_sum/sum_bgt_ytd))}</td>
									%endif

									<td class="total" colspan="1" style="text-align:right">${formatLang(sum_bgt_year, digits=get_digits(dp='Budget'))}</td>

									%if sum_bgt_year==0:
									<td class="total" colspan="1" style="text-align:right">${"%.2f" %(0)}</td>
									%else:
									<td class="total" colspan="1" style="text-align:right">${"%.2f" %(100*(sum_bgt_year-sum_act_ytd)/sum_bgt_year)}</td>
									%endif
								<tr>
							%endfor
							</table>
						</td>
					</tr>
				</table>

			%endfor
		%endfor
	</body>
</html>