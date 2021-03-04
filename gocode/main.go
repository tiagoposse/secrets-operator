package main

import (
	"flag"
	"fmt"
	"net/http"
)

var kubeconfig string

func init() {
	flag.StringVar(&kubeconfig, "kubeconfig", "", "path to Kubernetes config file")
	flag.Parse()
}

func runDaemon() {
	http.HandleFunc("/hello", nil)
	http.HandleFunc("/headers", nil)

	http.ListenAndServe(":8080", nil)

}

func main() {
	annotations := map[string]string{
		"secret.annotation.io": "teste",
		"secret.io.app":        "teste-app",
	}

	fmt.Print((annotations))
}
