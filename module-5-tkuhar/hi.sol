pragma solidity ^0.5.1;

library SafeMath {
    /**
     * @dev Multiplies two unsigned integers, reverts on overflow.
     */
    function mul(uint256 a, uint256 b) internal pure returns (uint256) {
        // Gas optimization: this is cheaper than requiring 'a' not being zero, but the
        // benefit is lost if 'b' is also tested.
        // See: https://github.com/OpenZeppelin/openzeppelin-solidity/pull/522
        if (a == 0) {
            return 0;
        }

        uint256 c = a * b;
        require(c / a == b);

        return c;
    }

    /**
     * @dev Integer division of two unsigned integers truncating the quotient, reverts on division by zero.
     */
    function div(uint256 a, uint256 b) internal pure returns (uint256) {
        // Solidity only automatically asserts when dividing by 0
        require(b > 0);
        uint256 c = a / b;
        // assert(a == b * c + a % b); // There is no case in which this doesn't hold

        return c;
    }

    /**
     * @dev Subtracts two unsigned integers, reverts on overflow (i.e. if subtrahend is greater than minuend).
     */
    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b <= a);
        uint256 c = a - b;

        return c;
    }

    /**
     * @dev Adds two unsigned integers, reverts on overflow.
     */
    function add(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 c = a + b;
        require(c >= a);

        return c;
    }

    /**
     * @dev Divides two unsigned integers and returns the remainder (unsigned integer modulo),
     * reverts when dividing by zero.
     */
    function mod(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b != 0);
        return a % b;
    }
}



contract GreenX{
    using SafeMath for uint256;
    mapping (address => uint256) private _balances;
    mapping (address => uint256) private _eth_balances;

    mapping (address => mapping (address => uint256)) private _allowed;
    uint256 private _totalSupply;

    uint256 private_sale_price  = 0.13 * 10**18;
    uint256 pre_sale_price      = 0.15 * 10**18;
    uint256 ico_1               = 0.17 * 10**18;
    uint256 ico_2               = 0.18 * 10**18;
    uint256 ico_3               = 0.20 * 10**18;
    uint256 dolar_per_ether     = 600  * 10**18;

    
    
    uint start_time = 0;
    
    
    
    bool pre_sale_state;
    bool private_sale_state;
    bool ico_state;
    
    uint curent_state = 0;
    /**
        0 - ICO not started
        1 - ICO phase 1
        2 - ICO phase 2
        3 - ICO phase 3
        4 - ICO ended
    */

    bool public token_transfering;

    
    string public name;                   //fancy name: eg Simon Bucks
    uint8 public decimals;                //How many decimals to show.
    string public symbol;                 //An identifier: eg SBX

    
    mapping (address => bool) private _private_investors;
    mapping (address => bool) public _investor_whitelist;
    
    address private _owner_address;
    address private _admin_address;
    address private _portal_address;
    address private _found_keeper_address;
    address private _founder_address;
    address private _team_address;
    address private _reserved_address;
    // address _team;

    

    constructor(address founder_address) public payable{
        name = "testoken";
        _found_keeper_address = founder_address;
        _owner_address = msg.sender;
        _totalSupply = 300000000;
        curent_state = 0;
        token_transfering = false;
        
        pre_sale_state = false;
        private_sale_state = false;
        ico_state = false;

    }

    /**
     * @dev Total number of tokens in existence
     */
    function totalSupply() public view returns (uint256) {
        return _totalSupply;
    }

    /**
     * @dev Gets the balance of the specified address.
     * @param owner The address to query the balance of.
     * @return An uint256 representing the amount owned by the passed address.
     */
    function balanceOf(address owner) external view returns (uint256) {
        return _balances[owner];
    }

    /**
     * @dev Function to check the amount of tokens that an owner allowed to a spender.
     * @param owner address The address which owns the funds.
     * @param spender address The address which will spend the funds.
     * @return A uint256 specifying the amount of tokens still available for the spender.
     */
    function allowance(address owner, address spender) external view returns (uint256) {
        return _allowed[owner][spender];
    }

    /**
     * @dev Transfer token for a specified address
     * @param to The address to transfer to.
     * @param value The amount to be transferred.
     */
    function transfer(address to, uint256 value) external returns (bool) {
        _transfer(msg.sender, to, value);
        return true;
    }

    /**
     * @dev Approve the passed address to spend the specified amount of tokens on behalf of msg.sender.
     * Beware that changing an allowance with this method brings the risk that someone may use both the old
     * and the new allowance by unfortunate transaction ordering. One possible solution to mitigate this
     * race condition is to first reduce the spender's allowance to 0 and set the desired value afterwards:
     * https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
     * @param spender The address which will spend the funds.
     * @param value The amount of tokens to be spent.
     */
    function approve(address spender, uint256 value) external returns (bool) {
        _approve(msg.sender, spender, value);
        return true;
    }

    /**
     * @dev Transfer tokens from one address to another.
     * Note that while this function emits an Approval event, this is not required as per the specification,
     * and other compliant implementations may not emit the event.
     * @param from address The address which you want to send tokens from
     * @param to address The address which you want to transfer to
     * @param value uint256 the amount of tokens to be transferred
     */
    function transferFrom(address from, address to, uint256 value) external returns (bool) {
        _transfer(from, to, value);
        _approve(from, msg.sender, _allowed[from][msg.sender].sub(value));
        return true;
    }

    /**
     * @dev Transfer token for a specified addresses
     * @param from The address to transfer from.
     * @param to The address to transfer to.
     * @param value The amount to be transferred.
     */
    function _transfer(address from, address to, uint256 value) internal {
        require(token_transfering);
        require(to != address(0));
        _balances[from] = _balances[from].sub(value);
        _balances[to] = _balances[to].add(value);
        // emit Transfer(from, to, value);
    }

    /**
     * @dev Approve an address to spend another addresses' tokens.
     * @param owner The address that owns the tokens.
     * @param spender The address that will spend the tokens.
     * @param value The number of tokens that can be spent.
     */
    function _approve(address owner, address spender, uint256 value) internal {
        require(spender != address(0));
        require(owner != address(0));

        _allowed[owner][spender] = value;
        // emit Approval(owner, spender, value);
    }

    function getCurrentState() external returns(uint, bool, bool, bool){
        _update_ICO_state();
        return (curent_state, private_sale_state , pre_sale_state,  ico_state);
    }
    
    function () external payable{
        require(_totalSupply > 0);
        require(ico_state || pre_sale_state || private_sale_state) ;
        issueToken(msg.sender);
    }
    
    
    
    function issueTokenForPrivateInvestor(address _client) private{
        _balances[_client] = SafeMath.add( _balances[_client] , SafeMath.div(msg.value, uint256((private_sale_price * 10**18) / dolar_per_ether)));
        _totalSupply = SafeMath.sub(_totalSupply, _balances[_client]);
        _eth_balances[_client] = SafeMath.add(_eth_balances[_client], msg.value);
    }

    function issueTokenForPresale(address _client) private{
        _balances[_client] = SafeMath.add( _balances[_client] , SafeMath.div (msg.value, uint256 ((pre_sale_price * 10**18) / dolar_per_ether)));
        _totalSupply = SafeMath.sub(_totalSupply, _balances[_client]);
        _eth_balances[_client] = SafeMath.add(_eth_balances[_client], msg.value);
    }
    
    function issueTokenForICO(address _client) private{
        if (curent_state == 1){
            _balances[_client] = SafeMath.add( _balances[_client] , SafeMath.div( msg.value, uint256((ico_1 * 10**18) / dolar_per_ether)));
        }
        else if (curent_state == 2){
            _balances[_client] = SafeMath.add( _balances[_client] , SafeMath.div( msg.value, uint256((ico_2 * 10**18) / dolar_per_ether)));
        }
        else if (curent_state == 3){
            _balances[_client] = SafeMath.add( _balances[_client] , SafeMath.div( msg.value, uint256((ico_3 * 10**18) / dolar_per_ether)));
        }
        else
            require(false, "Error in curent_state");
        _totalSupply = SafeMath.sub(_totalSupply, _balances[_client]);
        _eth_balances[_client] = SafeMath.add(_eth_balances[_client], msg.value);
    }
    
    function trackdownInvestedEther() private{}
    
    function issueToken(address _client) private{
        _update_ICO_state();
        if (_private_investors[_client] == true && private_sale_state){
            issueTokenForPrivateInvestor(_client);
        }
        else if (_investor_whitelist[_client] == true && pre_sale_state){
            issueTokenForPresale(_client);
        }
        else if (ico_state){
            issueTokenForICO(_client);
        }
        else
            require(false, "some Error");
    }
    
    
    
    
    function addToWhitelist(address _new_white_investor) external {
        require(
            msg.sender == _owner_address ||
            msg.sender == _admin_address ||
            msg.sender == _portal_address,
            "Permission denied"
        );
        _investor_whitelist[_new_white_investor] = true;
    }
     
    function removeFromWhitelist(address _del_white_investor) external {
        require(
            msg.sender == _owner_address ||
            msg.sender == _admin_address ||
            msg.sender == _portal_address,
            "Permission denied"
        );

        _investor_whitelist[_del_white_investor] = false;
    }

    function addPrivateInvestor(address _new_private_investor) external {
        require(
            msg.sender == _owner_address ||
            msg.sender == _admin_address ||
            msg.sender == _portal_address,
            "Permission denied"
        );
        _private_investors[_new_private_investor] = true;
    }
    
    function removePrivateInvestor(address _del_private_investor) external{
        require(
            msg.sender == _owner_address ||
            msg.sender == _admin_address ||
            msg.sender == _portal_address,
            "Permission denied"
        );

        _private_investors[_del_private_investor] = false;
    }
    
    
    
    
    function startPrivatSale() external{
        require(
            msg.sender == _owner_address ||
            msg.sender == _admin_address,
            "Permission denied"
        );
        private_sale_state = true;
    }
    
    function startPreSale() external{
        require(
            msg.sender == _owner_address ||
            msg.sender == _admin_address,
            "Permission denied"
        );
        pre_sale_state = true;
    }
    
    function endPreSale() external{
        require(
            msg.sender == _owner_address ||
            msg.sender == _admin_address,
            "Permission denied"
        );
        pre_sale_state = false;
    }
    
    function startICO() external{
        require(
            msg.sender == _owner_address ||
            msg.sender == _admin_address,
            "Permission denied"
        );
        pre_sale_state = false;
        private_sale_state = true;
        start_time = now;
        ico_state = true;
        curent_state = 1;
    }
    
    function _update_ICO_state() private {
        if (start_time == 0)
            return;
        else if (now - start_time > 540){
            ico_state = false;
            private_sale_state = false;
            pre_sale_state = false;
            curent_state = 4;
        }
        else if (now - start_time > 360){
            curent_state = 3;
        }
        else if (now - start_time > 180){
            curent_state = 2;
        }
    }

    function endICO() external{
        require(
            msg.sender == _owner_address ||
            msg.sender == _admin_address,
            "Permission denied"
        );
        ico_state = false;
        private_sale_state = false;
        pre_sale_state = false;
        curent_state = 4;
    }
    
    
    function setPrivateSalePrice(uint256 dollars_per_token) external{
         require(
            msg.sender == _owner_address ||
            msg.sender == _admin_address,
            "Permission denied"
        );
        private_sale_price = dollars_per_token;
    }
    
    function setPreSalePrice(uint256 dollars_per_token) external{
         require(
            msg.sender == _owner_address ||
            msg.sender == _admin_address,
            "Permission denied"
        );
        pre_sale_price = dollars_per_token;
    }
    
    function setICOPrice(uint256 stage1, uint256 stage2, uint256 stage3) external{
        require(
            msg.sender == _owner_address ||
            msg.sender == _admin_address,
            "Permission denied"
        );
        ico_1  = stage1;
        ico_2  = stage2;
        ico_3  = stage3;
    }
    
    
    function revokeToken() external{}
    
    
    
    function activateContract() external {
        require(msg.sender == _owner_address, "Permission denied");
    }
    
    function deactivateContract() external {
        require(msg.sender == _owner_address, "Permission denied");
        address(uint160 (_found_keeper_address)).transfer(address(this).balance);
    }
    
    
    function enableTokenTransfer() external {
        require(msg.sender == _owner_address, "Permission denied");
        token_transfering = true;
    }

    
    
    
    function changeFundKeeper(address _new_found_keeper) external {
        require(msg.sender == _owner_address, "Permission denied");
        _found_keeper_address = _new_found_keeper;
    }
    
    function changeAdminAddress(address _new_admin_address ) external {
        require(msg.sender == _owner_address, "Permission denied");        
        _admin_address = _new_admin_address;
    }
    
    function changePortalAddress(address _new_portal_address) external {
        require(msg.sender == _owner_address, "Permission denied");
        _portal_address = _new_portal_address;
    }
    
    function changeFounderAddress(address _new_founder_address) external {
        require(
            msg.sender == _owner_address ||
            msg.sender == _admin_address,
            "Permission denied"
        );

        _founder_address = _new_founder_address;
    }
    
    function changeTeamAddress(address _new_team_address) external {
        require(
            msg.sender == _owner_address ||
            msg.sender == _admin_address,
            "Permission denied"
        );

        _team_address = _new_team_address;
    }
    
    function changeReservedAddress(address _new_reserved_address) external{
        require(
            msg.sender == _owner_address ||
            msg.sender == _admin_address,
            "Permission denied"
        );

        _reserved_address = _new_reserved_address;
    }
    
    
    
    function allocateTokenForFounder() external {
        require(
            msg.sender == _owner_address ||
            msg.sender == _admin_address,
            "Permission denied"
        );
        _balances[_founder_address] = SafeMath.add(_balances[_founder_address] , 50000000);
    }
    
    function allocateTokenForTeam() external {
        require(
            msg.sender == _owner_address ||
            msg.sender == _admin_address,
            "Permission denied"
        );
        _balances[_team_address] = SafeMath.add(_balances[_team_address] , 30000000);
    }
    
    function moveAllAvailableToken(address _to) external {
        require(
            msg.sender == _owner_address ||
            msg.sender == _admin_address,
            "Permission denied"
        );
        _balances[_to] = SafeMath.add(_balances[_team_address] , _totalSupply);
        _totalSupply = SafeMath.sub(_totalSupply, _balances[_to]);
    }
    
    function allocateReservedToken(address _to) external {
        require(
            msg.sender == _owner_address ||
            msg.sender == _admin_address,
            "Permission denied"
        );
        _balances[_to] = SafeMath.add(_balances[_team_address] , 50000000);
    }
    
}

