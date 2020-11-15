import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup } from "@angular/forms";
import { Router } from "@angular/router";
import { RepositoryService } from "../services/repository.service";

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent implements OnInit {

  public registerForm : FormGroup;

  constructor(private readonly repositoryService: RepositoryService, private router: Router) { }

  ngOnInit(): void {
    this.registerForm = new FormGroup( {
      username: new FormControl(''),
      password: new FormControl('')
    });
  }

  public registerUser(registerFormValue) {
    this.repositoryService.create("addUser",registerFormValue).subscribe((res : any) => {
      if (res.msg !== 'Failed') {
        this.router.navigate(["/home"]);
      }
    })
  }

  public openLogin() {
    this.router.navigate(["/login"]);
  }

}
