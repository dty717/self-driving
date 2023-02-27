package selfDriving.web; 
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RequestParam;
import selfDriving.service.LocationService;

@Controller
public class LocationController {
 
    @Autowired
    LocationService locationService;

    //@PreAuthorize("hasRole('USER')")
    @RequestMapping(value = { "position"},produces = "application/json;charset=utf-8")
    @ResponseBody
    public String position(@RequestParam(name="x",required=false)Double x,@RequestParam(name="y",required=false)Double y,@RequestParam(name="deviceType",required=false)String deviceType) {
        locationService.position(x,y,deviceType);
        return "Hello World!";
    }
}
