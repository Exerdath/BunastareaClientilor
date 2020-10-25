import {Injectable} from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import { environment } from "src/environments/environment";

@Injectable()
export class RepositoryService{
    constructor(public httpClient:HttpClient){
    }



    public login(body:any){
        return this.httpClient.post('http://localhost:8080/login',body,{observe:'response'});
    }

    public logout() {
        return this.httpClient.post("http://localhost:8080/logout", null);
    }

    public isLoggedIn(){
        if(localStorage.getItem('user')!=null)
            return true;
        return false;
    }
    
    public getData(route: string, headers?:HttpHeaders){
        return this.httpClient.get(this.createCompleteRoute(route, environment.urlAddress));
    }

    public create(route:string, body:any, headers?:HttpHeaders){
        return this.httpClient.post(this.createCompleteRoute(route, environment.urlAddress), body);
    }

    public update(route:string, body:any,headers?:HttpHeaders){
        return this.httpClient.put(this.createCompleteRoute(route, environment.urlAddress), body);
    }

    public delete(route:string,headers?:HttpHeaders){
        return this.httpClient.delete(this.createCompleteRoute(route, environment.urlAddress));
    }


    public createCompleteRoute(route: string, envAddress: string) {
        return `${envAddress}/${route}`;
    }

}