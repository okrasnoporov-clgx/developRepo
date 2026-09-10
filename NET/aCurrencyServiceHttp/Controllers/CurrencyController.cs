using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Text.Json;
using System.Threading.Tasks;

namespace aCurrencyServiceHttp.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class CurrencyController : ControllerBase
    {

        [HttpGet]
        public ACurrency Get(string BankName, string CurrencyName)        
        {
            return GetCashRate(BankName, CurrencyName);
        }

        private string GetBankURL(string BankName) {

            var config = new ConfigurationBuilder().SetBasePath(AppDomain.CurrentDomain.BaseDirectory).AddJsonFile("appsettings.json").Build();            
            switch (BankName)
            {
                case "PrivatBank":
                    return config.GetSection("PrivatBank").GetValue<String>("PRIVAT_API_JSON_CURRENCY_CASH_url");
                case "PumbBank":
                    return config.GetSection("PumbBank").GetValue<String>("PUMB_API_JSON_CURRENCY_CASH_url");
                default:
                    return BankName;
            }

        }
        private string GetBankResponce(string BankName) {          

            string api_response_data = "";
            string Url = GetBankURL(BankName);
            WebRequest request = WebRequest.Create(Url);
            
            request.Method = "GET";
            HttpWebResponse response = (HttpWebResponse)request.GetResponse();

            using (StreamReader streamReader = new StreamReader(response.GetResponseStream()))
            {
                api_response_data = streamReader.ReadToEnd();
                streamReader.Close();
            }

            return api_response_data;        
        }
        private ACurrency GetCashRate(string BankName, string CurrencyName)
        {            
            var currentCurrencyList = JsonSerializer.Deserialize<List<ACurrency>>(GetBankResponce(BankName));

            foreach (ACurrency currency in currentCurrencyList)
            {
                if (currency.ccy == CurrencyName)
                {
                    return currency;

                } 
            } //foreach
            return null;
        }
    }
}
