(ns iswho.routes.home
  (:require
   [iswho.whois :as whois]
   [iswho.layout :as layout]
   [clojure.string :as st]
   [ring.util.response]
   [ring.util.http-response :as response]))

(defn request-page [{{:strs [domen options]} :form-params,
                     {token :token} :path-params,
                     :as request}]
  (let [result (whois/exec domen options token)]
    (layout/render request "request.html" result)))

(defn index-page [request]
  (layout/render request "index.html"))

(defn home-routes []
  [""
   ["/:token/" {:get index-page
               :post request-page}]])
