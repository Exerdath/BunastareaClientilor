import { Component, OnInit } from '@angular/core';
import { Router } from "@angular/router";
import { RepositoryService } from "../services/repository.service";

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {

  public averageSpent: number = 0.0;
  public suggestions: [] = [];
  public totalOrders: number = 0;
  public lastInvoices: [] = [];

  constructor(private readonly repositoryService: RepositoryService,
              private readonly router: Router) { }

  ngOnInit(): void {
    let customerId = JSON.parse(localStorage.getItem("user")).customerId;
    this.repositoryService.getData("avgbyid/"+customerId).subscribe((res : any) => {
      this.totalOrders = res.total_orders[0];
      this.averageSpent = res.avg_spend[0];
    });
    this.repositoryService.getData("suggestions/"+customerId).subscribe((res: any) => {
      this.suggestions = res;
    });
    this.repositoryService.getData("lastinvoicesbyid/"+customerId).subscribe((res: any) => {
      console.log(res);
      this.lastInvoices = res;
    });
  }

  public logOut() {
    localStorage.removeItem("user");
    this.router.navigate(["/login"])
  }

}
