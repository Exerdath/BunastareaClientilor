import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup } from "@angular/forms";
import { Router } from "@angular/router";
import { RepositoryService } from "../services/repository.service";

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {

  public loginForm : FormGroup;

  constructor(private readonly repositoryService: RepositoryService, private router: Router) { }

  ngOnInit(): void {
    if (localStorage.getItem("user")) {
      this.router.navigate(["/home"]);
    }
    this.loginForm = new FormGroup( {
      username: new FormControl(''),
      password: new FormControl('')
    });
  }

  public loginUser(loginFormValue) {
    this.repositoryService.create("login",loginFormValue).subscribe((res :any) => {
      localStorage.setItem("user", JSON.stringify(res));
      this.router.navigate(["/home"]);
    }, () => {
      alert("Wrong username or password");
    });
  }

  public openRegister() {
    this.router.navigate(["/register"]);
  }

}
