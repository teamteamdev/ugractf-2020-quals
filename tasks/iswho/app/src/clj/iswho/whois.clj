(ns iswho.whois
  (:require
   [ugractf.flag :as u]
   [me.raynes.conch.low-level :as sh]
   [clojure.java.io :as io]
   [clojure.string :as st]))

(def escaped-re #"^[^\n\r\"\',<>\[\];_$!@#%^&?*\(\)+=\\\/]+$")
(def flag-bs "[Init]\nCypher=GOST-12/Streeeeeebog\n\n[Secrets]\nFLAG=")

(defn flag [token]
  (let [tmp (System/getProperty "java.io.tmpdir")
        flag (io/file tmp "iswho" token "config.ini")]
    (when-not (.exists flag)
      (io/make-parents flag)
      (spit flag (str flag-bs (u/redeem-token token))))
    (.getParent flag)))

(def options "-l")
(def domain "a")
(def token "123")

(defn query [domain options token]
  (let [options (st/escape options {\' \space \" \space})]
    (sh/stream-to-string
     (sh/proc "su" "iswho" "-c"
              (str "bash -rc 'whois " options " " domain "'")
              :dir (flag token)) :out)))

(defn exec [domain options token]
  (cond
    (st/blank? domain)  {:error "Домена не существует!"}
    (st/blank? options) {:error "Опционально обязательно!"}
    (re-matches
     escaped-re domain)  {:result (query domain options token)}
    :else {:error "Хакер! Взлом детектива обнаружен!!!"}))
