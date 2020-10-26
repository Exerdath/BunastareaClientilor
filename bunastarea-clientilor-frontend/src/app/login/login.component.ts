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
    this.loginForm = new FormGroup( {
      username: new FormControl(''),
      password: new FormControl('')
    });
  }

  public loginUser(loginFormValue) {
    this.repositoryService.create("login",loginFormValue).subscribe((res :any) => {
      if (res.msg !== 'Failed') {
        localStorage.setItem("user",res.headers.get("authorization"));
        this.router.navigate(["/home"]);
      }
    })
  }

}
