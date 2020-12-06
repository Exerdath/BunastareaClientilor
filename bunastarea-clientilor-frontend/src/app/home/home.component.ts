import { Component, OnInit } from '@angular/core';
import { Router } from "@angular/router";
import { RepositoryService } from "../services/repository.service";

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {

  public averageSpent: number;
  public suggestions: [] = [];
  public totalOrders: number;
  public lastInvoices: [] = [];

  constructor(private readonly repositoryService: RepositoryService,
              private readonly router: Router) { }

  ngOnInit(): void {
    let user = JSON.parse(localStorage.getItem("user"));
    if (!user) {
      this.router.navigate(["/login"])
    }
    this.repositoryService.getData("avgbyid/"+user.customerId).subscribe((res : any) => {
      this.totalOrders = res[0].TotalOrders;
      this.averageSpent = res[0].AvgSpend;
    });
    this.repositoryService.getData("suggestions/"+user.customerId).subscribe((res: any) => {
      this.suggestions = res;
    });
    this.repositoryService.getData("lastinvoicesbyid/"+user.customerId).subscribe((res: any) => {
      this.lastInvoices = res;
    });
  }

  public logOut() {
    localStorage.removeItem("user");
    this.router.navigate(["/login"])
  }

}
